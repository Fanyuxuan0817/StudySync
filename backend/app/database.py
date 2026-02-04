from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

load_dotenv()

# DATABASE_URL = os.getenv(
#     "DATABASE_URL",
#     "postgresql://postgres:kaixin@localhost:5432/studysync"
# )


# 使用硬编码的连接字符串，避免编码问题
DATABASE_URL = "postgresql://postgres:kaixin@localhost:5432/studysync"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
