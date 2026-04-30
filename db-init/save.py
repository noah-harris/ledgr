from config import *
from db import get_connection
from sqlalchemy import text

RESTORE_POINT = RESTORE_POINTS_DIR / TIMESTAMP
RESTORE_POINT.mkdir(exist_ok=True)

def _get_current_csv_path(tbl:str) -> Path:
    path = RESTORE_POINT / f"{tbl}.csv"
    if not path.exists():
        with get_connection() as conn:
            pd.read_sql_query(text(f"SELECT TOP 0 * FROM [{tbl}]"), conn).to_csv(path, index=False)
    return path

def _save_table(tbl:str):
    with get_connection() as conn:
        df = pd.read_sql_query(text(f"SELECT * FROM [{tbl}]"), conn).fillna("")
    if df.empty:
        logger.warning(f"{tbl.upper()} has no data.")
    df.to_csv(_get_current_csv_path(tbl), index=False)
    logger.info(f"Saved {len(df)} records into {tbl} from {_get_current_csv_path(tbl)}")

for table_name in TABLES:
    if table_name in ["Payee", "Image"]:
        continue
    else:
        try:
            _save_table(table_name)
        except Exception as e:
            logger.error(f"Failed to save {table_name}: {e}")