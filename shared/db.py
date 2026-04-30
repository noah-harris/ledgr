from sqlalchemy import create_engine
from contextlib import contextmanager


def _connection_string(username: str, password: str, ip: str, port: str, database: str) -> str:
    return f"mssql+pyodbc://{username}:{password}@{ip},{port}/{database}?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"


@contextmanager
def transactional_connection(username: str, password: str, ip: str, port: str, database: str, timeout: int = 2, **engine_kwargs):
    cxnstr = _connection_string(username, password, ip, port, database)
    engine = create_engine(cxnstr, pool_pre_ping=True, connect_args={"timeout": timeout}, **engine_kwargs)
    conn = engine.connect()
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
def autocommit_connection(username: str, password: str, ip: str, port: str, database: str, timeout: int = 2, **engine_kwargs):
    cxnstr = _connection_string(username, password, ip, port, database)
    engine = create_engine(cxnstr, pool_pre_ping=True, connect_args={"timeout": timeout}, **engine_kwargs)
    conn = engine.connect()
    conn = conn.execution_options(isolation_level="AUTOCOMMIT")
    try:
        yield conn
    finally:
        conn.close()
        engine.dispose()
