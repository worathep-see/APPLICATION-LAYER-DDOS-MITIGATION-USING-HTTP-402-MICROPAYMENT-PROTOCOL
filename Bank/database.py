# Database Conection เชื่อมต่อกับ SQLite

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# สร้าง SQLite Database
DATABASE_URL = "sqlite:///bank.db"

# Engine ตัวจัดกการฐานข้อมูล
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)

# Session ใช้ทำ transaction 
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # สร้างตารางทั้งหมดในฐานข้อมูล
    Base.metadata.create_all(bind=engine)

def get_db():
    # สร้าง session ใหม่สำหรับการเชื่อมต่อฐานข้อมูล
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()