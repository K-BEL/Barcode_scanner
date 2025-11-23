"""Database initialization utilities."""
import mysql.connector
from mysql.connector import Error
from app.core.config import settings
from app.core.logging import logger


def create_database_if_not_exists():
    """Create MySQL database if it doesn't exist."""
    try:
        # Connect without specifying database
        conn = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            charset=settings.DB_CHARSET
        )
        
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{settings.DB_NAME}` "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Database '{settings.DB_NAME}' ready")
    except Error as e:
        logger.warning(f"Could not auto-create database (this is OK if database already exists): {e}")


def create_tables():
    """Create all database tables."""
    from app.core.database import get_db
    
    create_products_table = """
    CREATE TABLE IF NOT EXISTS products (
        barcode VARCHAR(255) PRIMARY KEY,
        product_name VARCHAR(255) NOT NULL,
        price FLOAT NOT NULL,
        quantity INT DEFAULT 1,
        details TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_product_name (product_name),
        INDEX idx_timestamp (timestamp)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    create_cart_table = """
    CREATE TABLE IF NOT EXISTS cart (
        id INT AUTO_INCREMENT PRIMARY KEY,
        barcode VARCHAR(255) NOT NULL,
        product_name VARCHAR(255) NOT NULL,
        price FLOAT NOT NULL,
        quantity INT DEFAULT 1,
        details TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_cart_barcode (barcode),
        INDEX idx_cart_timestamp (timestamp),
        FOREIGN KEY (barcode) REFERENCES products(barcode) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        modified_at DATETIME NULL,
        INDEX idx_user_name (name),
        INDEX idx_user_added_at (added_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    create_bills_table = """
    CREATE TABLE IF NOT EXISTS bills (
        id INT AUTO_INCREMENT PRIMARY KEY,
        bill_text TEXT NOT NULL,
        cashier_name VARCHAR(255) NULL,
        total_amount FLOAT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        file_path VARCHAR(500) NULL,
        INDEX idx_bill_created_at (created_at),
        INDEX idx_bill_cashier (cashier_name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute(create_products_table)
            cursor.execute(create_cart_table)
            cursor.execute(create_users_table)
            cursor.execute(create_bills_table)
            
            conn.commit()
            cursor.close()
            logger.info("Database tables initialized successfully")
    except Error as e:
        logger.error(f"Error creating tables: {e}")
        raise


def init_db():
    """Initialize database and tables."""
    # Create database if MySQL
    create_database_if_not_exists()
    
    # Create all tables
    create_tables()
