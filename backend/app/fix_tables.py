"""Script to fix MySQL tables by dropping and recreating them."""
import sys
from pathlib import Path

# Add the backend directory to Python path so imports work
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import mysql.connector
from app.core.config import settings
from app.core.logging import logger

def drop_and_recreate_tables():
    """Drop existing tables and recreate them with correct schema."""
    try:
        conn = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            charset=settings.DB_CHARSET
        )
        
        cursor = conn.cursor()
        
        # Drop tables in reverse order (respecting foreign keys)
        logger.info("Dropping existing tables...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("DROP TABLE IF EXISTS bills")
        cursor.execute("DROP TABLE IF EXISTS cart")
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS products")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        logger.info("Tables dropped successfully")
        cursor.close()
        conn.close()
        
        # Now recreate tables using the init_db function
        logger.info("Recreating tables...")
        from app.core.db_init import create_tables
        create_tables()
        
        logger.info("✅ Tables recreated successfully!")
        
    except Exception as e:
        logger.error(f"Error fixing tables: {e}")
        raise

if __name__ == "__main__":
    print("This will DROP all existing tables and recreate them.")
    print("All data will be lost!")
    response = input("Continue? (yes/no): ")
    if response.lower() == 'yes':
        drop_and_recreate_tables()
    else:
        print("Cancelled.")

