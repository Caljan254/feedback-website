"""
Migration: Add question_text column to question_responses table.
This stores the actual visible question label captured from the HTML form
at submission time, ensuring the admin always sees the correct
department-specific question text.

Run once: python migrate_add_question_text.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "feedback.db")

def run():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if column already exists
    cursor.execute("PRAGMA table_info(question_responses)")
    cols = [row[1] for row in cursor.fetchall()]

    if "question_text" in cols:
        print("✅ Column 'question_text' already exists in question_responses. Nothing to do.")
    else:
        cursor.execute(
            "ALTER TABLE question_responses ADD COLUMN question_text TEXT"
        )
        conn.commit()
        print("✅ Successfully added 'question_text' column to question_responses table.")

   
    # SQLite doesn't support dropping NOT NULL via ALTER TABLE, but new rows will just use NULL
    print("ℹ️  Note: question_id is now nullable for new submissions (SQLite-enforced at app level).")
    print(f"\n📋 Current question_responses columns: {cols + (['question_text'] if 'question_text' not in cols else [])}")

    conn.close()

if __name__ == "__main__":
    run()
