# Multi-Format Data Ingestion Service

import pandas as pd
import json
import chardet
import duckdb
from pathlib import Path
from typing import Dict, List, Tuple, Any
import sqlparse


class DataIngestor:
    """Handles ingestion of multiple data formats"""
    
    def __init__(self):
        self.supported_formats = {
            '.csv', '.xlsx', '.xls', '.json', '.sql', 
            '.parquet', '.tsv', '.txt'
        }
    
    def ingest(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Ingest data from file and return DataFrame + metadata
        
        Returns:
            (DataFrame, metadata_dict)
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension not in self.supported_formats:
            raise ValueError(f"Unsupported format: {extension}")
        
        # Route to appropriate handler
        if extension == '.csv':
            return self._ingest_csv(file_path)
        elif extension in ['.xlsx', '.xls']:
            return self._ingest_excel(file_path)
        elif extension == '.json':
            return self._ingest_json(file_path)
        elif extension == '.sql':
            return self._ingest_sql_dump(file_path)
        elif extension == '.parquet':
            return self._ingest_parquet(file_path)
        elif extension in ['.tsv', '.txt']:
            return self._ingest_delimited(file_path)
        
        raise ValueError(f"Handler not implemented for {extension}")
    
    def _detect_encoding(self, file_path: str) -> str:
        """Auto-detect file encoding"""
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read(100000))  # Sample first 100KB
        return result['encoding'] or 'utf-8'
    
    def _ingest_csv(self, file_path: str) -> Tuple[pd.DataFrame, Dict]:
        """Ingest CSV file"""
        encoding = self._detect_encoding(file_path)
        
        # Try to infer delimiter
        with open(file_path, 'r', encoding=encoding) as f:
            first_line = f.readline()
        
        delimiter = ',' if ',' in first_line else ';' if ';' in first_line else ','
        
        df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter)
        
        metadata = {
            'format': 'CSV',
            'encoding': encoding,
            'delimiter': delimiter,
            'columns': list(df.columns),
            'row_count': len(df)
        }
        
        return df, metadata
    
    def _ingest_excel(self, file_path: str) -> Tuple[pd.DataFrame, Dict]:
        """Ingest Excel file"""
        # Read all sheets
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        
        # If multiple sheets, read first one (can be enhanced later)
        df = pd.read_excel(file_path, sheet_name=sheet_names[0])
        
        metadata = {
            'format': 'Excel',
            'sheets': sheet_names,
            'active_sheet': sheet_names[0],
            'columns': list(df.columns),
            'row_count': len(df)
        }
        
        return df, metadata
    
    def _ingest_json(self, file_path: str) -> Tuple[pd.DataFrame, Dict]:
        """Ingest JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # Try to find the array
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    df = pd.DataFrame(value)
                    break
            else:
                # Single object - convert to single row
                df = pd.DataFrame([data])
        else:
            raise ValueError("Unsupported JSON structure")
        
        metadata = {
            'format': 'JSON',
            'structure': 'array' if isinstance(data, list) else 'object',
            'columns': list(df.columns),
            'row_count': len(df)
        }
        
        return df, metadata
    
    def _ingest_sql_dump(self, file_path: str) -> Tuple[pd.DataFrame, Dict]:
        """Ingest SQL dump file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Parse SQL statements
        statements = sqlparse.split(sql_content)
        
        # Create in-memory DuckDB and execute statements
        conn = duckdb.connect(':memory:')
        
        for stmt in statements:
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--'):
                try:
                    conn.execute(stmt)
                except Exception as e:
                    print(f"Warning: Could not execute statement: {e}")
        
        # Get table names
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        
        if not tables:
            raise ValueError("No tables found in SQL dump")
        
        # Read first table (enhance later for multi-table support)
        table_name = tables[0][0]
        df = conn.execute(f"SELECT * FROM {table_name}").df()
        
        metadata = {
            'format': 'SQL Dump',
            'tables': [t[0] for t in tables],
            'active_table': table_name,
            'columns': list(df.columns),
            'row_count': len(df)
        }
        
        conn.close()
        return df, metadata
    
    def _ingest_parquet(self, file_path: str) -> Tuple[pd.DataFrame, Dict]:
        """Ingest Parquet file"""
        df = pd.read_parquet(file_path)
        
        metadata = {
            'format': 'Parquet',
            'columns': list(df.columns),
            'row_count': len(df)
        }
        
        return df, metadata
    
    def _ingest_delimited(self, file_path: str) -> Tuple[pd.DataFrame, Dict]:
        """Ingest TSV or other delimited files"""
        encoding = self._detect_encoding(file_path)
        
        extension = Path(file_path).suffix.lower()
        delimiter = '\t' if extension == '.tsv' else ','
        
        df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter)
        
        metadata = {
            'format': 'Delimited',
            'encoding': encoding,
            'delimiter': delimiter,
            'columns': list(df.columns),
            'row_count': len(df)
        }
        
        return df, metadata
    
    def get_schema(self, df: pd.DataFrame) -> Dict[str, str]:
        """Extract schema from DataFrame"""
        schema = {}
        for col in df.columns:
            dtype = df[col].dtype
            
            # Map pandas dtype to SQL-like types
            if pd.api.types.is_integer_dtype(dtype):
                schema[col] = 'INTEGER'
            elif pd.api.types.is_float_dtype(dtype):
                schema[col] = 'FLOAT'
            elif pd.api.types.is_bool_dtype(dtype):
                schema[col] = 'BOOLEAN'
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                schema[col] = 'TIMESTAMP'
            else:
                schema[col] = 'TEXT'
        
        return schema
