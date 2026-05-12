import sqlalchemy
import os
import logging
from contextlib import contextmanager
logger = logging.getLogger("upload-images")

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
EXTERNAL_PORT = os.getenv("EXTERNAL_PORT")
INTERNTAL_PORT = os.getenv("INTERNAL_PORT")
HOST = os.getenv("HOST")


@contextmanager
def get_connection(database:str):
    CONN_STRING = f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{HOST},1433/{database}?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
    engine = sqlalchemy.create_engine(CONN_STRING, pool_pre_ping=True, connect_args={"timeout": 5})
    conn:sqlalchemy.engine.Connection = engine.connect()
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.commit()
        conn.close()
        engine.dispose()

@contextmanager
def get_autocommit_connection(database:str):
    CONN_STRING = f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{HOST},1433/{database}?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
    engine = sqlalchemy.create_engine(CONN_STRING, pool_pre_ping=True, connect_args={"timeout": 5})
    conn:sqlalchemy.engine.Connection = engine.connect()
    conn:sqlalchemy.engine.Connection = conn.execution_options(isolation_level="AUTOCOMMIT")
    try:
        yield conn
    finally:
        conn.close()
        engine.dispose()

