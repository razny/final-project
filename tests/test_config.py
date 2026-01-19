import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app
from app.database import get_db

# use a temporary SQLite file DB
TEST_DATABASE_URL = "sqlite:///./test_temp.db"  # file-based SQLite
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# override get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_test_db():
    Base.metadata.create_all(bind=engine)

def cleanup_test_db():
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./test_temp.db"):
        os.remove("./test_temp.db")

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

