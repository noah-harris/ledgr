import colorlog
import logging
import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

def make_logger(name: str) -> logging.Logger:
    root = logging.getLogger()
    if not root.handlers:
        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            fmt='%(log_color)s[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt="%H:%M:%S"
        ))
        root.addHandler(handler)
        root.setLevel(logging.DEBUG)
    return logging.getLogger(name)

# ==================== CREDENTIALS ====================
DOCKER_DB_USERNAME = os.getenv("DOCKER_DB_USERNAME")
DOCKER_DB_PASSWORD = os.getenv("DOCKER_DB_PASSWORD")
DOCKER_DB_IP = os.getenv("DOCKER_DB_IP")
DOCKER_DB_INTERNAL_PORT = os.getenv("DOCKER_DB_INTERNAL_PORT")
DOCKER_DB_EXTERNAL_PORT = os.getenv("DOCKER_DB_EXTERNAL_PORT")

# ==================== CONFIGURATION ====================
LOCALHOST = "127.0.0.1"
HOSTNAME = os.getenv("HOST_MACHINE_NAME")
TIMESTAMP = pd.Timestamp.now().strftime("%Y-%m-%d %H.%M.%S")
RESTORE_POINTS_DIR = Path("/app/data/restore/")
RESTORE_POINTS_DIR.mkdir(exist_ok=True, parents=True)
IMAGE_BASE_URL = os.getenv("IMAGE_DIRECTORY_LOCATION", "").rstrip("/")
SUPPORTED_IMAGE_FORMATS = ["png", "jpg", "jpeg", "gif", "bmp", "pdf"]
IMG_PATH = Path("/app/images")

# ==================== SCHEMA BUILD ORDER ====================
BUILD_ORDER = [
    (r"Security/Schemas", r"import"),
    (r"Programmability/Scalar-valued Functions", r"fn_StripNonAlphanumeric"),
    (r"Programmability/Stored Procedures", r"p_SelectAllTables"),
    (r"Tables", r"Currency"),
    (r"Tables", r"Users"),
    (r"Tables", r"ImageContentType"),
    (r"Tables", r"ImageSortStatusType"),
    (r"Tables", r"Image"),
    (r"Tables", r"ImageSort"),
    (r"Tables", r"Days"),
    (r"Tables", r"OrganizationType"),
    (r"Tables", r"Organization"),
    (r"Tables", r"AccountType"),
    (r"Tables", r"Account"),
    (r"Tables", r"MethodType"),
    (r"Tables", r"Method"),
    (r"Tables", r"AccountTypeMethodTypeTemplate"),
    (r"Tables", r"Payee"),
    (r"Tables", r"Invoice"),
    (r"Tables", r"InvoiceItemCategory"),
    (r"Tables", r"InvoiceItem"),
    (r"Tables", r"InvoiceTemplate"),
    (r"Tables", r"InvoiceTemplateItem"),
    (r"Tables", r"Statement"),
    (r"Tables", r"StatementItem"),
    (r"Views", r"v_Users"),
    (r"Views", r"v_Account"),
    (r"Views", r"v_Method"),
    (r"Views", r"v_Image"),
    (r"Views", r"v_Organization"),
    (r"Views", r"v_Payee"),
    (r"Views", r"v_Invoice"),
    (r"Views", r"v_Statement"),
    (r"Views", r"v_StatementItem"),
    (r"Views", r"v_InvoiceItemCategory"),
    (r"Views", r"v_InvoiceItem"),
    (r"Views", r"v_InvoiceTemplate"),
    (r"Views", r"v_InvoiceTemplateItem"),
    (r"Views", r"v_DisplayInvoice"),
    (r"Views", r"v_DisplayInvoiceItem"),
    (r"Views", r"v_DisplayStatementItem"),
    (r"Views", r"ve_Payee"),
    (r"Views", r"ve_StatementStatementItem"),
    (r"Programmability/Triggers", r"trg_ve_StatementStatementItem_Insert"),
    (r"Programmability/Triggers", r"trg_Image_Insert"),
    (r"Programmability/Triggers", r"trg_Account_Delete"),
    (r"Programmability/Triggers", r"trg_Account_Insert"),
    (r"Programmability/Triggers", r"trg_Organization_Delete"),
    (r"Programmability/Triggers", r"trg_Organization_Insert"),
    (r"Programmability/Triggers", r"trg_Users_Delete"),
    (r"Programmability/Triggers", r"trg_Users_Insert"),
]

TABLES = [tbl[1] for tbl in BUILD_ORDER if tbl[0] == "Tables"]