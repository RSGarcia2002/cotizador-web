import os
from contextlib import contextmanager
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor

_pool = None


def get_database_url() -> str:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("No se encontró DATABASE_URL en las variables de entorno.")
    return database_url


def init_pool(minconn: int = 1, maxconn: int = 10) -> None:
    global _pool
    if _pool is None:
        _pool = ThreadedConnectionPool(
            minconn=minconn,
            maxconn=maxconn,
            dsn=get_database_url()
        )


@contextmanager
def get_cursor(commit: bool = False):
    global _pool

    if _pool is None:
        init_pool()

    conn = _pool.getconn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cur
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
    finally:
        _pool.putconn(conn)


def fetch_all(query: str, params=None):
    with get_cursor() as cur:
        cur.execute(query, params or ())
        return cur.fetchall()


def fetch_one(query: str, params=None):
    with get_cursor() as cur:
        cur.execute(query, params or ())
        return cur.fetchone()


def execute(query: str, params=None):
    with get_cursor(commit=True) as cur:
        cur.execute(query, params or ())


def execute_returning_one(query: str, params=None):
    with get_cursor(commit=True) as cur:
        cur.execute(query, params or ())
        return cur.fetchone()