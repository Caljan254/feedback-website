from sqlalchemy import create_engine
from database import Base

engine = create_engine("mysql+pymysql://root:Aaamumo254%@localhost:3306/feedback_db")

Base.metadata.create_all(bind=engine)

print("✅ Feedback table created successfully.")