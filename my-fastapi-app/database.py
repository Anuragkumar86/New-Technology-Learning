import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()
# 1. Connection address matching the exact credentials from our Docker command

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in .env or environment!")

# DATABASE_URL = "postgresql+psycopg://admin:secretpassword@localhost:5432/shop_db"

# 2. Create the connection pool (Engine)
# echo=True prints the generated SQL commands in your terminal so you can see what happens
engine = create_engine(DATABASE_URL, echo=True)

# 3. Create a factory for generating database sessions (one per request)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 4. Base class that all our database table models will inherit from
class Base(DeclarativeBase):
    pass
