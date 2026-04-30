import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.config import *
from shared.config import make_logger

logger = make_logger('ledgr-db-seed')

PRIMARY_DESKTOP_LAN_IP = os.getenv("PRIMARY_DESKTOP_LAN_IP")
PRIMARY_SERVER_DB_USERNAME = os.getenv("PRIMARY_SERVER_DB_USERNAME")
PRIMARY_SERVER_DB_PASSWORD = os.getenv("PRIMARY_SERVER_DB_PASSWORD")
PRIMARY_SERVER_LAN_IP = os.getenv("PRIMARY_SERVER_LAN_IP")
PRIMARY_SERVER_DB_PORT = os.getenv("PRIMARY_SERVER_DB_PORT")
LINKED_SERVER_ADDRESSES = {
    "PRIMARY-SERVER": f"{LOCALHOST},{DOCKER_DB_EXTERNAL_PORT}",
    "PRIMARY-DESKTOP": f"{PRIMARY_DESKTOP_LAN_IP},{DOCKER_DB_EXTERNAL_PORT}"
}
