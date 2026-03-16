
from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def restore_missing_dept_ids():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.connect() as conn:
        print("Searching for feedback with missing department_id...")
        # Get the ID of the Directorate Of ICT
        result = conn.execute(text("SELECT id FROM departments WHERE name = 'Directorate Of ICT'")).fetchone()
        if not result:
            print("Directorate Of ICT not found. Cannot restore.")
            return
            
        ict_id = result[0]
        
        # Count missing ones
        count = conn.execute(text("SELECT COUNT(*) FROM feedback WHERE department_id IS NULL AND office = 'ict-services'")).scalar()
        if count > 0:
            print(f"Found {count} records with office 'ict-services' and missing department_id. Restoring to ID {ict_id}...")
            conn.execute(text("UPDATE feedback SET department_id = :dept_id WHERE department_id IS NULL AND office = 'ict-services'"), {"dept_id": ict_id})
            print("Successfully restored department IDs.")
            conn.commit()
        else:
            print("No missing department IDs found for 'ict-services'.")

if __name__ == "__main__":
    restore_missing_dept_ids()
