from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey , LargeBinary
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users' 
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)
    role = Column(String)

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    device_code = Column(String)
    op_date_time = Column(DateTime)
    curr = Column(String)
    amt = Column(Float)
    card_number = Column(String)
    file_id = Column(Integer, ForeignKey('imported_files.id'))

class ImportedFile(Base):
    __tablename__ = 'imported_files'

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    data = Column(LargeBinary)  # ← проверь, что поле именно так называется
    uploaded_at = Column(DateTime, default=datetime.utcnow)
