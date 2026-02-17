# Data Profiling and Analysis Service

import pandas as pd
import numpy as np
from typing import Dict, List, Any


class DataProfiler:
    """Generates comprehensive data profiles and insights"""
    
    def profile(self, df: pd.DataFrame, table_name: str = "data") -> Dict[str, Any]:
        """
        Generate comprehensive data profile
        
        Returns:
            {
                'overview': {...},
                'columns': {...},
                'data_quality': {...},
                'relationships': [...],
                'insights': [...]
            }
        """
        profile = {
            'overview': self._get_overview(df),
            'columns': self._profile_columns(df),
            'data_quality': self._assess_data_quality(df),
            'insights': self._generate_insights(df)
        }
        
        return self._sanitize_json(profile)

    def _sanitize_json(self, data: Any) -> Any:
        """Recursively sanitize data for JSON serialization"""
        if isinstance(data, dict):
            return {k: self._sanitize_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_json(v) for v in data]
        elif isinstance(data, float):
            if np.isnan(data) or np.isinf(data):
                return None
            return data
        elif isinstance(data, (np.integer, np.floating)):
            return self._sanitize_json(float(data) if isinstance(data, np.floating) else int(data))
        return data
    
    def _get_overview(self, df: pd.DataFrame) -> Dict:
        """Get high-level overview"""
        return {
            'row_count': len(df),
            'column_count': len(df.columns),
            'total_cells': df.size,
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 ** 2), 2),
            'duplicate_rows': df.duplicated().sum()
        }
    
    def _profile_columns(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Profile each column"""
        profiles = {}
        
        for col in df.columns:
            col_data = df[col]
            dtype = col_data.dtype
            
            col_profile = {
                'data_type': str(dtype),
                'null_count': int(col_data.isna().sum()),
                'null_percentage': round(col_data.isna().sum() / len(col_data) * 100, 2),
                'unique_count': int(col_data.nunique()),
                'unique_percentage': round(col_data.nunique() / len(col_data) * 100, 2)
            }
            
            # Numeric columns
            if pd.api.types.is_numeric_dtype(dtype):
                col_profile.update({
                    'min': float(col_data.min()) if not col_data.isna().all() else None,
                    'max': float(col_data.max()) if not col_data.isna().all() else None,
                    'mean': float(col_data.mean()) if not col_data.isna().all() else None,
                    'median': float(col_data.median()) if not col_data.isna().all() else None,
                    'std': float(col_data.std()) if not col_data.isna().all() else None,
                    'quartiles': {
                        'q25': float(col_data.quantile(0.25)) if not col_data.isna().all() else None,
                        'q50': float(col_data.quantile(0.50)) if not col_data.isna().all() else None,
                        'q75': float(col_data.quantile(0.75)) if not col_data.isna().all() else None
                    }
                })
            
            # Categorical/Text columns
            elif pd.api.types.is_object_dtype(dtype) or pd.api.types.is_string_dtype(dtype):
                value_counts = col_data.value_counts()
                top_values = value_counts.head(10).to_dict()
                
                col_profile.update({
                    'top_values': {str(k): int(v) for k, v in top_values.items()},
                    'avg_length': round(col_data.astype(str).str.len().mean(), 2) if not col_data.isna().all() else None,
                    'max_length': int(col_data.astype(str).str.len().max()) if not col_data.isna().all() else None
                })
            
            # DateTime columns
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                col_profile.update({
                    'min_date': str(col_data.min()) if not col_data.isna().all() else None,
                    'max_date': str(col_data.max()) if not col_data.isna().all() else None,
                    'date_range_days': (col_data.max() - col_data.min()).days if not col_data.isna().all() else None
                })
            
            profiles[col] = col_profile
        
        return profiles
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict:
        """Assess overall data quality"""
        total_cells = df.size
        null_cells = df.isna().sum().sum()
        duplicate_rows = df.duplicated().sum()
        
        # Calculate quality score (0-100)
        null_penalty = (null_cells / total_cells) * 50  # Up to 50 points
        duplicate_penalty = (duplicate_rows / len(df)) * 30 if len(df) > 0 else 0  # Up to 30 points
        
        quality_score = 100 - null_penalty - duplicate_penalty
        
        return {
            'overall_score': round(max(0, quality_score), 2),
            'total_nulls': int(null_cells),
            'null_percentage': round(null_cells / total_cells * 100, 2),
            'duplicate_rows': int(duplicate_rows),
            'duplicate_percentage': round(duplicate_rows / len(df) * 100, 2) if len(df) > 0 else 0,
            'completeness': round((1 - null_cells / total_cells) * 100, 2)
        }
    
    def _generate_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate human-readable insights"""
        insights = []
        
        # Overview insights
        insights.append(f"Dataset contains {len(df):,} rows and {len(df.columns)} columns")
        
        # Null insights
        null_cols = df.columns[df.isna().any()].tolist()
        if null_cols:
            insights.append(f"{len(null_cols)} columns have missing values: {', '.join(null_cols[:5])}")
        else:
            insights.append("✅ No missing values detected")
        
        # Duplicate insights
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            insights.append(f"⚠️ Found {dup_count} duplicate rows ({round(dup_count/len(df)*100, 1)}%)")
        
        # Numeric columns insights
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            insights.append(f"📊 {len(numeric_cols)} numeric columns available for analysis")
        
        # Categorical insights
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio < 0.05:  # Less than 5% unique
                insights.append(f"🏷️ '{col}' has only {df[col].nunique()} unique values - good for grouping")
        
        # Date columns
        date_cols = df.select_dtypes(include=['datetime64']).columns
        if len(date_cols) > 0:
            insights.append(f"📅 {len(date_cols)} date/time columns detected - time-series analysis possible")
        
        return insights
    
    def generate_suggested_queries(self, df: pd.DataFrame) -> List[str]:
        """Generate suggested natural language queries"""
        suggestions = []
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Basic aggregations
        if numeric_cols:
            suggestions.append(f"What is the average {numeric_cols[0]}?")
            suggestions.append(f"Show me the total {numeric_cols[0]}")
            
            if len(numeric_cols) > 1:
                suggestions.append(f"What is the sum of {numeric_cols[1]}?")
        
        # Grouping queries
        if categorical_cols and numeric_cols:
            suggestions.append(f"Show me {numeric_cols[0]} by {categorical_cols[0]}")
            suggestions.append(f"What are the top 10 {categorical_cols[0]} by {numeric_cols[0]}?")
        
        # Time-series
        if date_cols and numeric_cols:
            suggestions.append(f"Show me {numeric_cols[0]} over time")
            suggestions.append(f"What is the trend in {numeric_cols[0]}?")
        
        # Filtering
        if categorical_cols:
            suggestions.append(f"Show me all records where {categorical_cols[0]} is...")
        
        return suggestions[:8]  # Limit to 8 suggestions
