import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DOCKER_DB_USERNAME, DOCKER_DB_PASSWORD, DOCKER_DB_IP, DOCKER_DB_INTERNAL_PORT
from shared.db import transactional_connection, autocommit_connection


def get_connection(db: str = "ldr"):
    if db == "master":
        return autocommit_connection(DOCKER_DB_USERNAME, DOCKER_DB_PASSWORD, DOCKER_DB_IP, DOCKER_DB_INTERNAL_PORT, "master", fast_executemany=True)
    return transactional_connection(DOCKER_DB_USERNAME, DOCKER_DB_PASSWORD, DOCKER_DB_IP, DOCKER_DB_INTERNAL_PORT, db, fast_executemany=True)
