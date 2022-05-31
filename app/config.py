import os
from pathlib import Path

ENV: str = os.getenv('ENV', 'production').lower()
DEBUG: bool = ENV != 'production'
TESTING: bool = ENV == 'testing'
LOG_LEVEL: str = DEBUG and 'DEBUG' or 'INFO'

TIMEOUT: float = 0.1

NSJAIL_PATH: str = os.getenv('NSJAIL_PATH', '/usr/sbin/nsjail')
NSJAIL_CFG: str = os.getenv('NSJAIL_CFG', str(Path(__file__).parent / 'nsjail/nsjail.cfg'))

CGROUP_MEM_MAX: int = 32_000_000  # 32 MB
CGROUP_MEM_MEMSW_MAX: int = 0  # disabled
CGROUP_MEM_SWAP_MAX: int = 0  # swap is not allowed
CGROUP_PIDS_MAX: int = 2

CGROUP_MEM_MOUNT: str = '/sys/fs/cgroup/memory'
CGROUP_PIDS_MOUNT: str = '/sys/fs/cgroup/pids'
CGROUP_NET_CLS_MOUNT: str = '/sys/fs/cgroup/net_cls'
CGROUP_CPU_MOUNT: str = '/sys/fs/cgroup/cpu'

CGROUPV2_MOUNT: str = '/sys/fs/cgroup'
USE_CGROUPV2: bool = True
CGROUP_PARENT: str = 'NSJAIL'
