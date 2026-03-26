import sys
import os

# Add the current directory to sys.path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def add_tracking_id_column():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    print(f"Connecting to database...")
    with engine.connect() as connection:
        try:
            print("Checking if 'tracking_id' already exists in 'feedback' table...")
            # Use 'SHOW COLUMNS' for MySQL
            result = connection.execute(text("SHOW COLUMNS FROM feedback LIKE 'tracking_id'"))
            column_exists = result.fetchone() is not None
            
            if not column_exists:
                print("Adding 'tracking_id' column to 'feedback' table...")
                connection.execute(text("ALTER TABLE feedback ADD COLUMN tracking_id VARCHAR(20) UNIQUE AFTER anonymous"))
                connection.commit()
                print("[OK] Successfully added 'tracking_id' column.")
            else:
                print("[INFO] 'tracking_id' column already exists.")
                
        except Exception as e:
            print(f"[ERROR] Error during migration: {str(e)}")

if __name__ == "__main__":
    add_tracking_id_column()
