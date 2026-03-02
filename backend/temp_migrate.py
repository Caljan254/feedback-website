from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def migrate():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.connect() as conn:
        print("Migrating database...")
        # Add q_0 to q_4 columns to feedback table if they don't exist
        for i in range(5):
            col_name = f"q_{i}"
            try:
                conn.execute(text(f"ALTER TABLE feedback ADD COLUMN {col_name} VARCHAR(50) NULL"))
                print(f"Added column {col_name}")
            except Exception as e:
                print(f"Column {col_name} might already exist: {str(e)}")
        
        # Also ensure tracking_id exists (just in case)
        try:
            conn.execute(text("ALTER TABLE feedback ADD COLUMN tracking_id VARCHAR(20) UNIQUE NULL"))
            print("Added column tracking_id")
        except Exception as e:
            print("Column tracking_id might already exist")
            
        # Ensure department_id exists
        try:
            conn.execute(text("ALTER TABLE feedback ADD COLUMN department_id INTEGER NULL"))
            print("Added column department_id")
        except Exception as e:
            print("Column department_id might already exist")

        conn.commit()
        print("Migration complete!")

if __name__ == "__main__":
    migrate()
