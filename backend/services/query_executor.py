# Query Execution Service with DuckDB

import duckdb
import pandas as pd
from typing import Dict, Tuple, Any, Optional
import time
from datetime import datetime, timedelta


class QueryExecutor:
    """Executes SQL queries against uploaded datasets using DuckDB"""
    
    def __init__(self):
        self.connections = {}  # session_id -> duckdb_connection
        self.schema_cache = {}  # session_id -> cached schema
        self.last_access = {}  # session_id -> last access timestamp
        self.max_sessions = 10  # Maximum concurrent sessions
        self.session_timeout = 3600  # 1 hour idle timeout (seconds)
        self.max_schema_size = 10 * 1024 * 1024  # 10MB max schema size
    
    def register_dataframe(
        self, 
        session_id: int, 
        df: pd.DataFrame, 
        table_name: str = "data"
    ):
        """
        Register a pandas DataFrame as a DuckDB table for querying
        
        Args:
            session_id: Session identifier
            df: Data to register
            table_name: Name to use for the table
        """
        # Cleanup expired sessions before creating new ones
        self._cleanup_expired_sessions()
        
        # Check session limit
        if session_id not in self.connections and len(self.connections) >= self.max_sessions:
            # Remove oldest session
            oldest_session = min(self.last_access.keys(), key=lambda k: self.last_access[k])
            self.close_session(oldest_session)
        
        # Create or get connection for this session
        if session_id not in self.connections:
            self.connections[session_id] = duckdb.connect(':memory:')
        
        conn = self.connections[session_id]
        
        # Register the DataFrame
        conn.register(table_name, df)
        
        # Update last access time
        self.last_access[session_id] = datetime.now()
    
    def execute_query(
        self, 
        session_id: int, 
        query: str
    ) -> Tuple[bool, Optional[pd.DataFrame], Optional[str], float]:
        """
        Execute SQL query and return results
        
        Args:
            session_id: Session identifier
            query: SQL query to execute
            
        Returns:
            (success, result_df, error_message, execution_time_ms)
        """
        if session_id not in self.connections:
            return False, None, "No data registered for this session", 0.0
        
        conn = self.connections[session_id]
        
        # Update last access time
        self.last_access[session_id] = datetime.now()
        
        start_time = time.time()
        
        try:
            result = conn.execute(query).fetchdf()
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return True, result, None, execution_time
        
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_msg = str(e)
            
            return False, None, error_msg, execution_time
    
    def get_table_names(self, session_id: int) -> list:
        """Get all table names registered in session"""
        if session_id not in self.connections:
            return []
        
        conn = self.connections[session_id]
        
        try:
            tables = conn.execute("SHOW TABLES").fetchall()
            return [t[0] for t in tables]
        except:
            return []
    
    def get_table_schema(self, session_id: int, table_name: str) -> Dict[str, str]:
        """Get schema for a specific table"""
        if session_id not in self.connections:
            return {}
        
        conn = self.connections[session_id]
        
        try:
            schema = conn.execute(f"DESCRIBE {table_name}").fetchdf()
            return dict(zip(schema['column_name'], schema['column_type']))
        except:
            return {}
    
    
    def _cleanup_expired_sessions(self):
        """Remove sessions that have been idle for too long"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, last_time in self.last_access.items():
            if (current_time - last_time).total_seconds() > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            print(f"Cleaning up expired session: {session_id}")
            self.close_session(session_id)
    
    def close_session(self, session_id: int):
        """Close DuckDB connection for session"""
        if session_id in self.connections:
            self.connections[session_id].close()
            del self.connections[session_id]
        
        # Clean up cache and access tracking
        if session_id in self.schema_cache:
            del self.schema_cache[session_id]
        if session_id in self.last_access:
            del self.last_access[session_id]
    
    def clear_all_sessions(self):
        """Close all connections"""
        for conn in self.connections.values():
            conn.close()
        self.connections.clear()
    
    def __del__(self):
        """Cleanup on deletion"""
        self.clear_all_sessions()


# Global instance
query_executor = QueryExecutor()
