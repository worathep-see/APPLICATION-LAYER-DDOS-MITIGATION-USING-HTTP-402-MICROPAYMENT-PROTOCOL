from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

# --- จุดที่แก้ไข: หาที่อยู่ไฟล์จริง (Absolute Path) ---
# หาว่าไฟล์ database.py นี้อยู่ที่โฟลเดอร์ไหนในเครื่อง Server
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# สั่งให้สร้าง bank.db ไว้ในโฟลเดอร์เดียวกันเลย (จะไม่มีทางหลงที่แน่นอน)
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'bank.db')}"
# --------------------------------------------------

# Engine ตัวจัดการฐานข้อมูล
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