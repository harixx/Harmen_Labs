"""
Database configuration and models for Agentic Solutions website
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ContactSubmission(Base):
    """Model for storing contact form submissions"""
    __tablename__ = "contact_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    form_type = Column(String(50), nullable=False)  # general, consultation, project
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    company = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    service = Column(String(100), nullable=True)
    budget = Column(String(50), nullable=True)
    timeline = Column(String(50), nullable=True)
    message = Column(Text, nullable=True)
    challenges = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Boolean, default=False)

class NewsletterSubscription(Base):
    """Model for storing newsletter subscriptions"""
    __tablename__ = "newsletter_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    industry = Column(String(100), nullable=True)
    subscribed_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()