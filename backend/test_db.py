from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from config import Config

# Using Config for database URL
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

try:
    engine.connect()
    print("[OK] Successfully connected to the database!")
except OperationalError as e:
    print("[ERROR] Failed to connect:", str(e))