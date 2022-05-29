import os
from pathlib import Path

ENV: str = os.getenv('ENV', 'production').lower()
DEBUG: bool = ENV != 'production'
TESTING: bool = ENV == 'testing'
LOG_LEVEL: str = DEBUG and 'DEBUG' or 'INFO'

TIMEOUT: float = 0.1

NSJAIL_PATH: str = os.getenv('NSJAIL_PATH', '/usr/sbin/nsjail')
NSJAIL_CFG: str = os.getenv('NSJAIL_CFG', str(Path(__file__).parent / 'nsjail.cfg'))

CGROUP_MEM_MAX: int = 32_000_000  # 32 MB
CGROUP_PIDS_MAX: int = 1
