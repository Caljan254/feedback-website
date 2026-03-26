from sqlalchemy import create_engine
from database import Base
from config import Config

# Using Config for database URL
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

Base.metadata.create_all(bind=engine)

print("[OK] Feedback table created successfully.")