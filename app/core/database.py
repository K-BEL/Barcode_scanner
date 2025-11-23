"""MySQL database connection and management."""
import mysql.connector
from mysql.connector import pooling, Error
from contextlib import contextmanager
from typing import Generator
import threading

from app.core.config import settings
from app.core.logging import logger


class MySQLConnectionPool:
    """MySQL connection pool manager."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        """Initialize MySQL connection pool."""
        if MySQLConnectionPool._instance is not None:
            raise Exception("MySQLConnectionPool is a singleton!")
        
        self.pool_config = {
            'pool_name': 'barcode_scanner_pool',
            'pool_size': 10,
            'pool_reset_session': True,
            'host': settings.DB_HOST,
            'port': settings.DB_PORT,
            'user': settings.DB_USER,
            'password': settings.DB_PASSWORD,
            'database': settings.DB_NAME,
            'charset': settings.DB_CHARSET,
            'autocommit': False,
            'raise_on_warnings': True,
            'use_unicode': True,
            'collation': 'utf8mb4_unicode_ci'
        }
        
        try:
            self.pool = pooling.MySQLConnectionPool(**self.pool_config)
            logger.info(f"MySQL connection pool created: {settings.DB_NAME}@{settings.DB_HOST}")
        except Error as e:
            logger.error(f"Error creating MySQL connection pool: {e}")
            raise
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def get_connection(self):
        """Get a connection from the pool."""
        try:
            return self.pool.get_connection()
        except Error as e:
            logger.error(f"Error getting connection from pool: {e}")
            raise


# Initialize connection pool
try:
    connection_pool = MySQLConnectionPool.get_instance()
except Exception as e:
    logger.error(f"Failed to initialize MySQL connection pool: {e}")
    connection_pool = None


@contextmanager
def get_db() -> Generator[mysql.connector.MySQLConnection, None, None]:
    """
    Context manager to get MySQL database connection.
    Yields a connection and ensures it's closed after use.
    
    Usage:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products")
            results = cursor.fetchall()
            conn.commit()
    """
    if connection_pool is None:
        raise RuntimeError("MySQL connection pool not initialized")
    
    conn = None
    try:
        conn = connection_pool.get_connection()
        yield conn
    except Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()


def init_db():
    """Initialize database tables."""
    from app.core.db_init import init_db as _init_db
    _init_db()
