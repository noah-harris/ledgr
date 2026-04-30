import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.config import *
from shared.config import make_logger

logger = make_logger('ledgr-db-init')