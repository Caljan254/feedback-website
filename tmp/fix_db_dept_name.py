
from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def fix_dept_name():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.connect() as conn:
        print("Checking for 'ICT Services'...")
        # Check if ICT Services exists
        result = conn.execute(text("SELECT id FROM departments WHERE name = 'ICT Services'")).fetchone()
        if result:
            print(f"Found 'ICT Services' with ID {result[0]}. Updating to 'Directorate Of ICT'...")
            conn.execute(text("UPDATE departments SET name = 'Directorate Of ICT' WHERE id = :id"), {"id": result[0]})
            print("Successfully updated department name.")
            
            # Also update any admin users that might have the old name in their fullname string 
            # (though that's less critical for filtering, it's good for display)
            conn.execute(text("UPDATE users SET fullname = REPLACE(fullname, 'ICT Services', 'Directorate Of ICT') WHERE department_id = :id"), {"id": result[0]})
            print("Updated admin user display names.")
            conn.commit()
        else:
            print("Could not find 'ICT Services' in departments table. Maybe it was already updated or has a different name.")
            
            # Let's list all departments to be sure
            depts = conn.execute(text("SELECT id, name FROM departments")).fetchall()
            print("\nCurrent departments in DB:")
            for d in depts:
                print(f"ID {d[0]}: {d[1]}")

if __name__ == "__main__":
    fix_dept_name()
