import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ENV: str = os.getenv('ENV', 'production').lower()
if ENV not in ('production', 'development', 'testing'):
    raise ValueError(
        f'ENV={ENV} is not valid. ' "It should be 'production', 'development' or 'testing'"
    )
DEBUG: bool = ENV != 'production'
TESTING: bool = ENV == 'testing'

os.environ['LOGURU_LEVEL'] = os.getenv('LOG_LEVEL') or (DEBUG and 'DEBUG') or 'INFO'
os.environ['LOGURU_DEBUG_COLOR'] = '<fg #777>'
REQUEST_ID_LENGTH = int(os.getenv('REQUEST_ID_LENGTH', '8'))
PYGMENTS_STYLE = os.getenv('PYGMENTS_STYLE', 'github-dark')

TIMEOUT: float = 0.2

NSJAIL_PATH: str = os.getenv('NSJAIL_PATH', '/usr/sbin/nsjail')
NSJAIL_CFG: str = os.getenv('NSJAIL_CFG', str(Path(__file__).parent / 'nsjail/nsjail.cfg'))

CGROUP_MEM_MAX: int = 64_000_000  # 64 MB
CGROUP_MEM_MEMSW_MAX: int = 0  # disabled
CGROUP_MEM_SWAP_MAX: int = 0  # swap is not allowed
CGROUP_PIDS_MAX: int = 12  # rustc needs that

CGROUP_MEM_MOUNT: str = '/sys/fs/cgroup/memory'
CGROUP_PIDS_MOUNT: str = '/sys/fs/cgroup/pids'
CGROUP_NET_CLS_MOUNT: str = '/sys/fs/cgroup/net_cls'
CGROUP_CPU_MOUNT: str = '/sys/fs/cgroup/cpu'

CGROUPV2_MOUNT: str = '/sys/fs/cgroup'
CGROUP_PARENT: str = 'NSJAIL'
