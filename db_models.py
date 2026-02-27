from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Get SQLite database path
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "/Users/netcom/bmsupa/biodb.db")
SQLITE_URL = f"sqlite:///{SQLITE_DB_PATH}"

# Create engine and session
engine = create_engine(SQLITE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class AttData(Base):
    __tablename__ = "ATT_TABLE"
    
    id = Column(Integer, primary_key=True)
    emp_id = Column(Integer)
    emp_name = Column(String)
    time_stamp = Column(String)
    
    def __repr__(self):
        return f"<AttData(emp_id={self.emp_id}, name={self.emp_name}, time={self.time_stamp})>"