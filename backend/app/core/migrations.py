"""Database migration utilities for schema updates."""
import mysql.connector
from mysql.connector import Error
from app.core.database import get_db
from app.core.logging import logger


def migrate_database():
    """Run database migrations to add new columns and tables."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Add new columns to products table if they don't exist
            try:
                cursor.execute("ALTER TABLE products ADD COLUMN reorder_point INT DEFAULT 0")
                logger.info("Added reorder_point column to products table")
            except Error as e:
                if "Duplicate column name" not in str(e):
                    logger.warning(f"Could not add reorder_point column: {e}")
            
            try:
                cursor.execute("ALTER TABLE products ADD COLUMN category_id INT NULL")
                logger.info("Added category_id column to products table")
            except Error as e:
                if "Duplicate column name" not in str(e):
                    logger.warning(f"Could not add category_id column: {e}")
            
            # Create categories table
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS categories (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL UNIQUE,
                        description TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_category_name (name)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                logger.info("Created categories table")
            except Error as e:
                logger.warning(f"Could not create categories table: {e}")
            
            # Add foreign key constraint for category_id if it doesn't exist
            try:
                cursor.execute("""
                    ALTER TABLE products 
                    ADD CONSTRAINT fk_product_category 
                    FOREIGN KEY (category_id) REFERENCES categories(id) 
                    ON DELETE SET NULL
                """)
                logger.info("Added foreign key constraint for category_id")
            except Error as e:
                if "Duplicate foreign key" not in str(e) and "already exists" not in str(e):
                    logger.warning(f"Could not add foreign key constraint: {e}")
            
            # Add new columns to bills table
            # Add subtotal as nullable first, then update existing records, then make NOT NULL
            try:
                # Check if column exists
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'bills' 
                    AND COLUMN_NAME = 'subtotal'
                """)
                col_exists = cursor.fetchone()['count'] > 0
                
                if not col_exists:
                    # Add as nullable first
                    cursor.execute("ALTER TABLE bills ADD COLUMN subtotal FLOAT NULL")
                    logger.info("Added subtotal column to bills table (nullable)")
                    
                    # Update existing bills
                    cursor.execute("UPDATE bills SET subtotal = total_amount WHERE subtotal IS NULL")
                    logger.info("Updated existing bills with subtotal values")
                    
                    # Now make it NOT NULL
                    cursor.execute("ALTER TABLE bills MODIFY COLUMN subtotal FLOAT NOT NULL DEFAULT 0")
                    logger.info("Made subtotal column NOT NULL")
            except Error as e:
                if "Duplicate column name" not in str(e):
                    logger.warning(f"Could not add subtotal column: {e}")
            
            try:
                cursor.execute("ALTER TABLE bills ADD COLUMN discount_amount FLOAT DEFAULT 0")
                logger.info("Added discount_amount column to bills table")
            except Error as e:
                if "Duplicate column name" not in str(e):
                    logger.warning(f"Could not add discount_amount column: {e}")
            
            try:
                cursor.execute("ALTER TABLE bills ADD COLUMN tax_amount FLOAT DEFAULT 0")
                logger.info("Added tax_amount column to bills table")
            except Error as e:
                if "Duplicate column name" not in str(e):
                    logger.warning(f"Could not add tax_amount column: {e}")
            
            try:
                cursor.execute("ALTER TABLE bills ADD COLUMN payment_method VARCHAR(50) DEFAULT 'cash'")
                logger.info("Added payment_method column to bills table")
            except Error as e:
                if "Duplicate column name" not in str(e):
                    logger.warning(f"Could not add payment_method column: {e}")
            
            # Create stock_history table
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stock_history (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        barcode VARCHAR(255) NOT NULL,
                        quantity_change INT NOT NULL,
                        previous_quantity INT NOT NULL,
                        new_quantity INT NOT NULL,
                        reason VARCHAR(255) NOT NULL,
                        user_id VARCHAR(36) NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_stock_barcode (barcode),
                        INDEX idx_stock_created_at (created_at),
                        INDEX idx_stock_user (user_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                logger.info("Created stock_history table")
            except Error as e:
                logger.warning(f"Could not create stock_history table: {e}")
            
            # Create user_auth table
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_auth (
                        user_id VARCHAR(36) PRIMARY KEY,
                        username VARCHAR(255) NOT NULL UNIQUE,
                        password_hash VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        last_login DATETIME NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_auth_username (username),
                        INDEX idx_auth_email (email)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                logger.info("Created user_auth table")
            except Error as e:
                logger.warning(f"Could not create user_auth table: {e}")
            
            # Create user_roles table
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_roles (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL,
                        role VARCHAR(50) NOT NULL DEFAULT 'cashier',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_user_role_user (user_id),
                        INDEX idx_user_role_role (role),
                        UNIQUE KEY unique_user_role (user_id, role)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                logger.info("Created user_roles table")
            except Error as e:
                logger.warning(f"Could not create user_roles table: {e}")
            
            # Add indexes if they don't exist
            try:
                cursor.execute("CREATE INDEX idx_reorder_point ON products(reorder_point)")
            except Error:
                pass
            
            try:
                cursor.execute("CREATE INDEX idx_category_id ON products(category_id)")
            except Error:
                pass
            
            try:
                cursor.execute("CREATE INDEX idx_bill_payment_method ON bills(payment_method)")
            except Error:
                pass
            
            # Ensure all existing bills have proper subtotal (already handled above, but double-check)
            try:
                cursor.execute("UPDATE bills SET subtotal = total_amount WHERE subtotal IS NULL OR subtotal = 0")
                affected = cursor.rowcount
                if affected > 0:
                    logger.info(f"Updated {affected} existing bills with subtotal values")
            except Error as e:
                # Column might not exist yet or already updated
                if "Unknown column" not in str(e):
                    logger.warning(f"Could not update bills subtotal: {e}")
            
            conn.commit()
            cursor.close()
            logger.info("Database migrations completed successfully")
    except Error as e:
        logger.error(f"Error running migrations: {e}")
        raise

