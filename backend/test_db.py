from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Make sure there is only one '@' symbol — separates user:pass from host
engine = create_engine("mysql+pymysql://root:Aaamumo254%@localhost:3306/feedback_db")

try:
    engine.connect()
    print("✅ Successfully connected to the database!")
except OperationalError as e:
    print("❌ Failed to connect:", str(e))