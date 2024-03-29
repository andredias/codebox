from pathlib import Path

from loguru import logger

from ..config import (
    CGROUP_CPU_MOUNT,
    CGROUP_MEM_MOUNT,
    CGROUP_NET_CLS_MOUNT,
    CGROUP_PARENT,
    CGROUP_PIDS_MOUNT,
    CGROUPV2_MOUNT,
)


def get_version() -> int:
    """
    Examine the filesystem and return the guessed cgroup version.

    Fall back to use_cgroupv2 in the NsJail config if either both v1 and v2 seem to be enabled,
    or neither seem to be enabled.
    """
    cgroup_mounts = (
        CGROUP_MEM_MOUNT,
        CGROUP_PIDS_MOUNT,
        CGROUP_NET_CLS_MOUNT,
        CGROUP_CPU_MOUNT,
        CGROUP_PIDS_MOUNT,
    )
    v1_exists = any(Path(mount).exists() for mount in cgroup_mounts)

    controllers_path = Path(CGROUPV2_MOUNT, 'cgroup.controllers')
    v2_exists = controllers_path.exists()

    version = v2_exists and 2 or v1_exists and 1 or 0
    if version == 0:
        logger.warning(
            f'Neither the cgroupv1 controller mounts, nor {str(controllers_path)!r} exists. '
            'Either cgroup_xxx_mount and cgroupv2_mount are misconfigured, or all '
            'corresponding v1 controllers are disabled on the system. '
            'Falling back to the use_cgroupv2 NsJail setting.'
        )
        version = 2
    return version


def init() -> int:
    """Determine the cgroup version, initialise the cgroups for NsJail, and return the version."""
    version = get_version()
    if version == 1:
        init_v1()
    else:
        init_v2()

    return version


def init_v1() -> None:
    """
    Create a PID and memory cgroup for NsJail to use as the parent cgroup for each controller.

    NsJail doesn't do this automatically because it requires privileges NsJail usually doesn't
    have.
    """
    pids = Path(CGROUP_PIDS_MOUNT, CGROUP_PARENT)
    mem = Path(CGROUP_MEM_MOUNT, CGROUP_PARENT)

    pids.mkdir(parents=True, exist_ok=True)
    mem.mkdir(parents=True, exist_ok=True)


def init_v2() -> None:
    """Ensure cgroupv2 children have controllers enabled."""
    cgroup_mount = Path(CGROUPV2_MOUNT)

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
