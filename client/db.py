import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DOCKER_DB_USERNAME, DOCKER_DB_PASSWORD, LOCALHOST, DOCKER_DB_EXTERNAL_PORT
from shared.db import transactional_connection


def get_connection():
    return transactional_connection(DOCKER_DB_USERNAME, DOCKER_DB_PASSWORD, LOCALHOST, DOCKER_DB_EXTERNAL_PORT, "ldr", timeout=5)
