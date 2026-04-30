import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import *
from shared.db import transactional_connection


def get_connection():
    return transactional_connection(DOCKER_DB_USERNAME, DOCKER_DB_PASSWORD, DOCKER_DB_IP, DOCKER_DB_INTERNAL_PORT, "ldr", fast_executemany=True)
