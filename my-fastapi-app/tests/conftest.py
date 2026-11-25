import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base          # Your DeclarativeBase from database.py
from main import app, get_db       # Your FastAPI app and original get_db dependency
from models import ProductDB       # Your ProductDB table model


import os
from dotenv import load_dotenv

load_dotenv()

# 1. Point to the TEST Docker container on port 5433 (NOT 5432!)
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+psycopg://admin:secretpassword@localhost:5433/shop_test_db")

test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# 2. FIXTURE 1: Creates fresh tables in port 5433 before EACH test, and drops them after!
@pytest.fixture(scope="function")
def db_session():
    # BEFORE 'yield' (Runs before the test starts):
    Base.metadata.create_all(bind=test_engine)   # Creates empty 'products' table in shop_test_db
    db = TestingSessionLocal()                   # Opens a session to shop_test_db

    try:
        yield db                                 # Hands 'db' to the test (and pauses here!)
    finally:
        # AFTER 'yield' (Runs after the test finishes—even if the test failed!):
        db.close()                               # Closes the test DB session
        Base.metadata.drop_all(bind=test_engine) # Deletes all tables so next test starts 100% clean!


# 3. FIXTURE 2: Gives tests a TestClient wired to 'db_session' (port 5433)
@pytest.fixture(scope="function")
def client(db_session):
    # Replacement function that FastAPI will use instead of main.py's get_db()
    def override_get_db():
        yield db_session

    # Swap real DB (5432) -> test DB (5433)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client                        # Hands 'test_client' to your test function

    # Reset overrides after the test finishes
    app.dependency_overrides.clear()


# 4. FIXTURE 3: Pre-inserts 1 sample product into shop_test_db for tests that need existing data
@pytest.fixture(scope="function")
def sample_product(db_session) -> ProductDB:
    product = ProductDB(
        name="iPhone 16",
        category="Electronics",
        price=800.0,
        in_stock=True,
        stock=10,
        rating=4.8,
        tags=["smartphone", "apple"],  # Works natively because we're using real PostgreSQL!
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product