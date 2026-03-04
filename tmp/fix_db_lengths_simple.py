import pymysql

def fix_db_error():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='Aaamumo254%',
            database='feedback_db'
        )
        with conn.cursor() as cursor:
            print("Expanding column lengths to prevent 'Data too long' errors...")
            
            # Change rating and q_0-q_4 to VARCHAR(255)
            cols = ['rating', 'q_0', 'q_1', 'q_2', 'q_3', 'q_4']
            for col in cols:
                sql = f"ALTER TABLE feedback MODIFY COLUMN {col} VARCHAR(255) NULL"
                cursor.execute(sql)
                print(f"✅ Modified {col}")
            
        conn.commit()
        conn.close()
        print("✅ Database schema updated successfully.")
    except Exception as e:
        print(f"❌ Error updating database: {e}")

if __name__ == "__main__":
    fix_db_error()
