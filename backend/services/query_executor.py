# Query Execution Service with DuckDB

import duckdb
import pandas as pd
from typing import Dict, Tuple, Any, Optional
import time


class QueryExecutor:
    """Executes SQL queries against uploaded datasets using DuckDB"""
    
    def __init__(self):
        self.connections = {}  # session_id -> duckdb_connection
    
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
        # Create or get connection for this session
        if session_id not in self.connections:
            self.connections[session_id] = duckdb.connect(':memory:')
        
        conn = self.connections[session_id]
        
        # Register the DataFrame
        conn.register(table_name, df)
    
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
    
    def close_session(self, session_id: int):
        """Close DuckDB connection for session"""
        if session_id in self.connections:
            self.connections[session_id].close()
            del self.connections[session_id]
    
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
