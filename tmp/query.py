import sqlite3
import pprint

try:
    conn = sqlite3.connect('backend/feedback.db')
    cur = conn.cursor()
    print("--- Departments ---")
    for row in cur.execute('SELECT id, name FROM departments'):
        print(row)
    
    print("\n--- VC Office Feedback ---")
    for row in cur.execute('SELECT id, office, department_id, message FROM feedback WHERE office LIKE "%vice%" OR office LIKE "%vc%" OR office LIKE "%Vice Chancellor%"'):
        print(row)
        
    print("\n--- All feedback office distribution ---")
    for row in cur.execute('SELECT office, department_id, count(*) FROM feedback GROUP BY office, department_id'):
        print(row)
except Exception as e:
    print(e)
