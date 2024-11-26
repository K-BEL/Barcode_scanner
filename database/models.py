from sqlalchemy import create_engine, Column, String, Float, Integer, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()

# Define the Products table
class Product(Base):
    __tablename__ = 'products'
    barcode = Column(String, primary_key=True)
    product_name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    details = Column(String, default="to fill")
    timestamp = Column(DateTime, default=datetime.utcnow)

# Define the Cart table
class Cart(Base):
    __tablename__ = 'cart'
    id = Column(Integer, primary_key=True, autoincrement=True)
    barcode = Column(String, ForeignKey('products.barcode'), nullable=False)
    quantity = Column(Integer, default=1)

# Define the Users table
class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, nullable=True)

# Define the Bills table
class Bill(Base):
    __tablename__ = 'bills'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bill_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# SQLite connection setup
DATABASE_URL = "sqlite:///barcode_scanner.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)
