# Database Models for Talk-to-Data AI

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Session(Base):
    """User sessions for managing multiple datasets"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default={})
    
    # Relationships
    data_sources = relationship("DataSource", back_populates="session", cascade="all, delete-orphan")
    query_history = relationship("QueryHistory", back_populates="session", cascade="all, delete-orphan")


class DataSource(Base):
    """Uploaded data sources (files/databases)"""
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)  # csv, excel, json, sql_dump, database
    file_path = Column(String(500))
    schema = Column(JSON, default={})  # {table_name: {columns: [...], types: [...]}}
    row_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="data_sources")
    data_profile = relationship("DataProfile", back_populates="data_source", uselist=False, cascade="all, delete-orphan")


class DataProfile(Base):
    """Automatically generated data analysis and insights"""
    __tablename__ = "data_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False, unique=True)
    statistics = Column(JSON, default={})  # {column_name: {mean, median, std, min, max, nulls, uniques}}
    insights = Column(Text)  # LLM-generated summary
    data_quality_score = Column(Float)  # 0-100
    suggested_queries = Column(JSON, default=[])  # ["query1", "query2"]
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    data_source = relationship("DataSource", back_populates="data_profile")


class QueryHistory(Base):
    """Natural language query history with results"""
    __tablename__ = "query_history"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    natural_language_query = Column(Text, nullable=False)
    generated_sql = Column(Text)
    execution_status = Column(String(50))  # success, error, refined
    error_message = Column(Text)
    result_summary = Column(JSON, default={})  # {row_count, columns, preview}
    visualization_type = Column(String(50))  # table, bar, line, pie, scatter
    created_at = Column(DateTime, default=datetime.utcnow)
    execution_time_ms = Column(Float)
    
    # Relationships
    session = relationship("Session", back_populates="query_history")
