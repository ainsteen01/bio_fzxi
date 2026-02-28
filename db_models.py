from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# DATABASE CONFIG
# --------------------------------------------------

SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "/tmp/biodb.db")  # Writable path
SQLITE_URL = f"sqlite:///{SQLITE_DB_PATH}"

# ✅ IMPORTANT CHANGE: add check_same_thread=False
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# ✅ Better session config
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ✅ Modern import style
Base = declarative_base()

# --------------------------------------------------
# MODEL
# --------------------------------------------------

class AttData(Base):
    __tablename__ = "ATT_TABLE"
    
    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(Integer, index=True)
    emp_name = Column(String)
    time_stamp = Column(String, index=True)
    
    def __repr__(self):
        return f"<AttData(emp_id={self.emp_id}, name={self.emp_name}, time={self.time_stamp})>"


# ✅ Ensure table exists
Base.metadata.create_all(bind=engine)
