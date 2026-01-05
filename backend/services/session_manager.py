# Session Management Service

from sqlalchemy.orm import Session
from models import Session as SessionModel, DataSource, QueryHistory, DataProfile
from typing import List, Optional, Dict
from datetime import datetime


class SessionManager:
    """Manages user sessions and data sources"""
    
    def create_session(self, db: Session, name: str) -> SessionModel:
        """Create a new session"""
        session = SessionModel(name=name, metadata={})
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    def get_session(self, db: Session, session_id: int) -> Optional[SessionModel]:
        """Get session by ID"""
        return db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    def list_sessions(self, db: Session) -> List[SessionModel]:
        """List all sessions"""
        return db.query(SessionModel).order_by(SessionModel.updated_at.desc()).all()
    
    def delete_session(self, db: Session, session_id: int):
        """Delete session and all associated data"""
        session = self.get_session(db, session_id)
        if session:
            db.delete(session)
            db.commit()
    
    def add_data_source(
        self,
        db: Session,
        session_id: int,
        name: str,
        source_type: str,
        file_path: str,
        schema: Dict,
        row_count: int
    ) -> DataSource:
        """Add a data source to session"""
        data_source = DataSource(
            session_id=session_id,
            name=name,
            source_type=source_type,
            file_path=file_path,
            schema=schema,
            row_count=row_count
        )
        db.add(data_source)
        
        # Update session timestamp
        session = self.get_session(db, session_id)
        if session:
            session.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(data_source)
        return data_source
    
    def add_data_profile(
        self,
        db: Session,
        data_source_id: int,
        statistics: Dict,
        insights: str,
        quality_score: float,
        suggested_queries: List[str]
    ) -> DataProfile:
        """Add data profile for a data source"""
        profile = DataProfile(
            data_source_id=data_source_id,
            statistics=statistics,
            insights=insights,
            data_quality_score=quality_score,
            suggested_queries=suggested_queries
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    
    def add_query_history(
        self,
        db: Session,
        session_id: int,
        nl_query: str,
        sql_query: str,
        status: str,
        error_msg: Optional[str],
        result_summary: Dict,
        viz_type: str,
        exec_time_ms: float
    ) -> QueryHistory:
        """Add query to history"""
        query = QueryHistory(
            session_id=session_id,
            natural_language_query=nl_query,
            generated_sql=sql_query,
            execution_status=status,
            error_message=error_msg,
            result_summary=result_summary,
            visualization_type=viz_type,
            execution_time_ms=exec_time_ms
        )
        db.add(query)
        
        # Update session timestamp
        session = self.get_session(db, session_id)
        if session:
            session.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(query)
        return query
    
    def get_query_history(
        self, 
        db: Session, 
        session_id: int, 
        limit: int = 50
    ) -> List[QueryHistory]:
        """Get query history for session"""
        return (
            db.query(QueryHistory)
            .filter(QueryHistory.session_id == session_id)
            .order_by(QueryHistory.created_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_data_sources(self, db: Session, session_id: int) -> List[DataSource]:
        """Get all data sources for session"""
        return (
            db.query(DataSource)
            .filter(DataSource.session_id == session_id)
            .all()
        )


# Global instance
session_manager = SessionManager()
