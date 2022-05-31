from pathlib import Path

from loguru import logger

from .config_pb2 import NsJailConfig  # type: ignore


def get_version(config: NsJailConfig) -> int:
    """
    Examine the filesystem and return the guessed cgroup version.

    Fall back to use_cgroupv2 in the NsJail config if either both v1 and v2 seem to be enabled,
    or neither seem to be enabled.
    """
    cgroup_mounts = (
        config.cgroup_mem_mount,
        config.cgroup_pids_mount,
        config.cgroup_net_cls_mount,
        config.cgroup_cpu_mount,
    )
    v1_exists = any(Path(mount).exists() for mount in cgroup_mounts)

    controllers_path = Path(config.cgroupv2_mount, 'cgroup.controllers')
    v2_exists = controllers_path.exists()

    config_version = 2 if config.use_cgroupv2 else 1

    if v1_exists and v2_exists:
        # Probably hybrid mode. Use whatever is set in the config.
        return config_version
    elif v1_exists:
        if config_version == 2:
            logger.warning(
                'NsJail is configured to use cgroupv2, but only cgroupv1 was detected on the '
                'system. Either use_cgroupv2 or cgroupv2_mount is incorrect. Snekbox is unable '
                'to override use_cgroupv2. If NsJail has been configured to use cgroups, then '
                'it will fail. In such case, please correct the config manually.'
            )
        return 1
    elif v2_exists:
        return 2
    else:
        logger.warning(
            f'Neither the cgroupv1 controller mounts, nor {str(controllers_path)!r} exists. '
            'Either cgroup_xxx_mount and cgroupv2_mount are misconfigured, or all '
            'corresponding v1 controllers are disabled on the system. '
            'Falling back to the use_cgroupv2 NsJail setting.'
        )
        return config_version


def init(config: NsJailConfig) -> int:
    """Determine the cgroup version, initialise the cgroups for NsJail, and return the version."""
    version = get_version(config)
    if version == 1:
        init_v1(config)
    else:
        init_v2(config)

    return version


def init_v1(config: NsJailConfig) -> None:
    """
    Create a PID and memory cgroup for NsJail to use as the parent cgroup for each controller.

    NsJail doesn't do this automatically because it requires privileges NsJail usually doesn't
    have.
    """
    pids = Path(config.cgroup_pids_mount, config.cgroup_pids_parent)
    mem = Path(config.cgroup_mem_mount, config.cgroup_mem_parent)

    pids.mkdir(parents=True, exist_ok=True)
    mem.mkdir(parents=True, exist_ok=True)


def init_v2(config: NsJailConfig) -> None:
    """Ensure cgroupv2 children have controllers enabled."""
    cgroup_mount = Path(config.cgroupv2_mount)

    # If the root's subtree_control already has some controllers enabled,
    # no further action is necessary.
    if (cgroup_mount / 'cgroup.subtree_control').read_text().strip():
        return

    # Move all processes from the cgroupv2 mount to a child cgroup.
    # This is necessary to be able to write to subtree_control in the parent later.
    # Otherwise, a write operation would yield a "device or resource busy" error.
    init_cgroup = cgroup_mount / 'init'
    init_cgroup.mkdir(parents=True, exist_ok=True)

    procs = (cgroup_mount / 'cgroup.procs').read_text().split()
    for proc in procs:
        (init_cgroup / 'cgroup.procs').write_text(proc)

    # Enable all available controllers for child cgroups.
    # This also retroactively enables controllers for children that already exist,
    # including the "init" child created just before.
    controllers = (cgroup_mount / 'cgroup.controllers').read_text().split()
    for controller in controllers:
        (cgroup_mount / 'cgroup.subtree_control').write_text(f'+{controller}')
