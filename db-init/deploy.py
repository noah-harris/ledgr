from db import get_connection
from sqlalchemy import text
from config import *
import pandas as pd
import requests
from html.parser import HTMLParser
from urllib.parse import unquote
from pathlib import Path
from datetime import datetime
import numpy as np


class _DirectoryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.filenames = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name, val in attrs:
                if name == 'href' and val and not val.startswith('?') and not val.startswith('/'):
                    self.filenames.append(val)
def create():
    logger.debug("RECREATING DATABASE [ldr]...")
    with get_connection(db="master") as conn:
        conn.execute(text("CREATE DATABASE [ldr]"))

    logger.debug("CREATING DATABASE OBJECTS...")
    with get_connection() as conn:
        for f in BUILD_ORDER:
            logger.debug(f"Creating {f[1]}...")
            with open(f"db-init/{f[0]}/{f[1]}.sql", "r", encoding="utf-8-sig") as sql_file:
                sql = sql_file.read()
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception as e:
                logger.critical(f"Error creating {f[1]}: {e}", exc=type(e))


def load():

    def _get_csv_dtypes(table_name, schema='dbo'):
        SQL_TO_PANDAS_DTYPE = {
            'bit': np.bool_,
            'tinyint': np.int8,
            'smallint': np.int16,
            'int': np.int32,
            'bigint': np.int64,
            'decimal': np.float64,
            'numeric': np.float64,
            'money': np.float64,
            'smallmoney': np.float64,
            'float': np.float64,
            'real': np.float32,
            'char': str,
            'varchar': str,
            'text': str,
            'nchar': str,
            'nvarchar': str,
            'ntext': str,
            'xml': str,
            'date': str,
            'datetime': str,
            'datetime2': str,
            'smalldatetime': str,
            'datetimeoffset': str,
            'time': str,
            'binary': bytes,
            'varbinary': bytes,
            'image': bytes,
            'uniqueidentifier': str,
            'sql_variant': str,
        }
        DATATYPE_QUERY = """
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = :table AND TABLE_SCHEMA = :schema
            ORDER BY ORDINAL_POSITION
        """
        query = text(DATATYPE_QUERY)
        with get_connection() as conn:
            rows = conn.execute(query, {"table": table_name, "schema": schema}).fetchall()
        if not rows:
            raise ValueError(f"No columns found for [{schema}].[{table_name}].")
        return {col: SQL_TO_PANDAS_DTYPE.get(sql_type.lower(), str) for col, sql_type in rows}

    def _get_latest_restore_point() -> Path | None:
        dirs = []
        for item in RESTORE_POINTS_DIR.iterdir():
            if item.is_dir() and item.name != TIMESTAMP:
                try:
                    dt = datetime.strptime(item.name, "%Y-%m-%d %H.%M.%S")
                    dirs.append((item, dt))
                except ValueError:
                    pass
        saves = sorted(dirs, key=lambda x: x[1], reverse=True)
        return saves[0][0] if saves else None

    restore_point = _get_latest_restore_point()

    if not restore_point:
        logger.warning("No restore points found.")
        return

    for table in TABLES:
        
        try:
            csv_path = restore_point / f"{table}.csv"
            match table:

                case "Image":
                    resp = requests.get(IMAGE_BASE_URL, timeout=5)
                    resp.raise_for_status()
                    parser = _DirectoryParser()
                    parser.feed(resp.text)
                    for filename in sorted(parser.filenames):
                        filename = unquote(filename)
                        filetype = Path(filename).suffix.lower().lstrip(".")
                        stem = Path(filename).stem
                        if filetype not in SUPPORTED_IMAGE_FORMATS:
                            logger.debug(f"Skipping unsupported file: {filename}")
                            continue
                        with get_connection() as conn:
                            conn.execute(
                                text("INSERT INTO [v_Image] ([FileName], [FileType]) VALUES (:FileName, :FileType)"),
                                parameters={"FileName": stem, "FileType": filetype}
                            )
                        logger.info(f"Inserted image: {filename}")


                case "ImageSort":
                    df = pd.read_csv(csv_path, index_col=False)
                    with get_connection() as conn:
                        df.to_sql(name="ImageSort", con=conn, schema="import", if_exists="replace", index=False)
                        conn.execute(text("""
                            UPDATE ims
                            SET 
                                ims.[StatusType] = imp.[StatusType],
                                ims.[ContentType] = imp.[ContentType]
                            FROM [dbo].[ImageSort] AS ims
                            JOIN [import].[ImageSort] AS imp ON ims.[ImageId] = imp.[ImageId]
                        """))
                    logger.info(f"Loaded {len(df)} records into ImageSort from {csv_path}")

                case "Payee":
                    continue

                case _:
                    if not csv_path.exists():
                        logger.warning(f"No data file found for {table} in latest restore point.")
                        return
                    
                    df = pd.read_csv(csv_path, dtype=_get_csv_dtypes(table)).fillna("")
                    df = df.replace({"": None})
                    with get_connection() as conn:
                        df.to_sql(name=table, con=conn, schema="dbo", if_exists="append", index=False)
                    logger.info(f"Loaded {len(df)} records into {table} from {csv_path}")

        except Exception as e:
            logger.error(f"Failed to load {table}: {e}")

create()
load()