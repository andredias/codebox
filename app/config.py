import os
from pathlib import Path

DEBUG: bool = os.getenv('ENV', 'development') == 'development'

TIME_LIMIT: float = 1

NSJAIL_PATH: str = os.getenv('NSJAIL_PATH', '/usr/sbin/nsjail')
NSJAIL_CFG: str = os.getenv('NSJAIL_CFG', str(Path(__file__).parent / 'nsjail.cfg'))

CGROUP_MEMORY_PATH: Path = Path('/sys/fs/cgroup/memory')
CGROUP_PIDS_PATH: Path = Path('/sys/fs/cgroup/pids')

CGROUP_MEM_MAX: int = 32_000_000  # 32 MB
CGROUP_PIDS_MAX: int = 1

# Limit of stdout bytes we consume before terminating nsjail
OUTPUT_MAX: int = 100_000
READ_CHUNK_SIZE: int = 10_000  # chars
