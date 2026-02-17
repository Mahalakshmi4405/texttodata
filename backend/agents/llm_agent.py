# LLM Agent for Natural Language Query Understanding

import google.generativeai as genai
from config import get_settings
import pandas as pd
from typing import Dict, Optional, Tuple
import json
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where, Token
from sqlparse.tokens import Keyword, DML
from agents.prompts import (
    SYSTEM_PROMPT, 
    QUERY_REFINEMENT_PROMPT, 
    INSIGHTS_GENERATION_PROMPT,
    VISUALIZATION_TYPE_PROMPT
)



class LLMAgent:
    """Google Gemini-powered agent for NL to SQL translation"""
    
    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        # Dynamically find an available model
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            # Prefer gemini-1.5-flash if available, else take the first one
            if 'models/gemini-1.5-flash' in available_models:
                model_name = 'gemini-1.5-flash'
            elif 'models/gemini-pro' in available_models:
                model_name = 'gemini-pro'
            elif available_models:
                model_name = available_models[0].replace('models/', '')
                print(f"Warning: Default models not found. Using fallback: {model_name}")
            else:
                raise ValueError("No generative models found for this API key")
            
            print(f"Using Google Gemini Model: {model_name}")
            self.model = genai.GenerativeModel(model_name)
        except Exception as e:
            print(f"Error listing models: {e}. Defaulting to 'gemini-pro'")
            self.model = genai.GenerativeModel('gemini-pro')
    
    def _get_response_text(self, response) -> str:
        """Safely extract text from response, handling blocked/empty cases"""
        try:
            if response.parts:
                return response.text.strip()
            
            # Use safety_ratings buffer instead of direct lookup if needed, 
            # or just inspection of the object structure if available.
            # But the most common issue is blocked content.
            if hasattr(response, 'prompt_feedback'):
                if response.prompt_feedback.block_reason:
                    raise ValueError(f"Response blocked: {response.prompt_feedback.block_reason}")
            
            # If we are here, it might be an empty response or standard finish reason
            # finish_reason 1 is STOP, but if no parts, it's weird.
            # finish_reason 4 is SAFETY.
            
            # Simple fallback
            if response.candidates:
                if response.candidates[0].finish_reason == 1: # STOP
                   # Sometimes models return empty string
                   return ""
                
            raise ValueError(f"Empty response from LLM (Finish Reason: {response.candidates[0].finish_reason if response.candidates else 'Unknown'})")
            
        except Exception as e:
            # Fallback for when structure is unexpected
            if "requires the response to contain a valid `Part`" in str(e):
                 raise ValueError(f"LLM Response Error: Model returned no content. This usually happens due to safety filters or empty output. Details: {e}")
            raise e

    def generate_sql(
        self, 
        question: str, 
        schema: Dict[str, str],
        sample_data: pd.DataFrame,
        table_name: str = "data"
    ) -> str:
        """
        Convert natural language question to SQL
        
        Args:
            question: User's natural language query
            schema: Dict of column_name -> data_type
            sample_data: Sample DataFrame for context
            table_name: Name of the table in DuckDB
            
        Returns:
            SQL query string
        """
        # Build schema description
        schema_desc = f"Table: {table_name}\n"
        schema_desc += "\n".join([f"  - {col}: {dtype}" for col, dtype in schema.items()])
        
        # Get sample rows
        sample_rows = sample_data.head(3).to_string(index=False)
        
        # Build full prompt
        system_prompt = SYSTEM_PROMPT.format(
            schema=schema_desc,
            sample_data=sample_rows
        )
        
        # Generate SQL
        full_prompt = f"{system_prompt}\n\nUser question: {question}\n\nSQL query:"
        
        response = self.model.generate_content(full_prompt)
        sql_query = self._get_response_text(response)
        
        # Clean up the response
        sql_query = self._clean_sql(sql_query)
        
        return sql_query
    
    def refine_query(
        self,
        question: str,
        failed_query: str,
        error_message: str,
        schema: Dict[str, str],
        sample_data: pd.DataFrame
    ) -> str:
        """
        Refine a failed SQL query
        
        Args:
            question: Original natural language query
            failed_query: SQL query that failed
            error_message: Error message from execution
            schema: Database schema
            sample_data: Sample data
            
        Returns:
            Refined SQL query
        """
        schema_desc = "\n".join([f"  - {col}: {dtype}" for col, dtype in schema.items()])
        
        prompt = QUERY_REFINEMENT_PROMPT.format(
            error_message=error_message,
            question=question,
            failed_query=failed_query
        )
        
        prompt += f"\n\nSchema:\n{schema_desc}\n\nSQL query:"
        
        response = self.model.generate_content(prompt)
        refined_query = self._get_response_text(response)
        
        return self._clean_sql(refined_query)
    
    def generate_insights(
        self,
        profile: Dict,
        max_insights: int = 5
    ) -> str:
        """
        Generate natural language insights from data profile
        
        Args:
            profile: Data profile dictionary
            max_insights: Maximum number of insights (default 5)
            
        Returns:
            Human-readable insights text (concise bullet points)
        """
        # Format column stats
        col_stats = []
        for col, stats in list(profile.get('columns', {}).items())[:10]:  # Limit to 10 cols
            if 'mean' in stats:
                col_stats.append(f"{col}: mean={stats.get('mean', 'N/A')}, std={stats.get('std', 'N/A')}")
            elif 'top_values' in stats:
                top = list(stats['top_values'].keys())[:3]
                col_stats.append(f"{col}: top values = {', '.join(top)}")
        
        col_stats_str = "\n".join(col_stats)
        
        # Format quality issues
        quality = profile.get('data_quality', {})
        quality_issues = f"- Null percentage: {quality.get('null_percentage', 0)}%\n"
        quality_issues += f"- Duplicate rows: {quality.get('duplicate_rows', 0)}"
        
        prompt = INSIGHTS_GENERATION_PROMPT.format(
            row_count=profile.get('overview', {}).get('row_count', 0),
            column_count=profile.get('overview', {}).get('column_count', 0),
            quality_score=quality.get('overall_score', 0),
            column_stats=col_stats_str,
            quality_issues=quality_issues
        )
        
        response = self.model.generate_content(prompt)
        insights_text = self._get_response_text(response)
        
        # Post-process: Ensure concise bullet points
        insights_text = self._format_concise_insights(insights_text, max_insights)
        
        return insights_text

    def _format_concise_insights(self, insights_text: str, max_insights: int = 5) -> str:
        """
        Post-process insights to ensure they are concise and properly formatted
        
        Args:
            insights_text: Raw insights from LLM
            max_insights: Maximum number of bullet points
            
        Returns:
            Formatted concise insights
        """
        # Split into lines and find bullet points
        lines = insights_text.strip().split('\n')
        bullets = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and titles
            if not line or 'AI Insights' in line or 'Summary' in line:
                continue
            
            # Remove bullet markers and clean up
            line = line.lstrip('•-*').strip()
            
            if line:
                # Truncate to 100 characters if needed
                if len(line) > 100:
                    line = line[:97] + '...'
                bullets.append(line)
        
        # Limit to max_insights
        bullets = bullets[:max_insights]
        
        # Format as bullet points
        if bullets:
            return '\n'.join([f'• {bullet}' for bullet in bullets])
        else:
            return "• Data quality analysis complete\n• Ready for querying"

    
    def suggest_visualization(
        self,
        query: str,
        result_df: pd.DataFrame
    ) -> str:
        """
        Suggest best visualization type for query result
        
        Args:
            query: SQL query executed
            result_df: Result DataFrame
            
        Returns:
            Visualization type: table, bar, line, pie, scatter, heatmap
        """
        if len(result_df) > 100:
            return "table"
        
        if len(result_df) == 0:
            return "table"
        
        columns = list(result_df.columns)
        sample = result_df.head(5).to_dict(orient='records')
        
        prompt = VISUALIZATION_TYPE_PROMPT.format(
            query=query,
            columns=columns,
            row_count=len(result_df),
            sample_result=json.dumps(sample, default=str)
        )
        
        response = self.model.generate_content(prompt)
        try:
            viz_type = self._get_response_text(response).lower()
        except ValueError:
            # Fallback if AI fails to suggest
            viz_type = "table"
        
        # Validate
        valid_types = ['table', 'bar', 'line', 'pie', 'scatter', 'heatmap']
        if viz_type not in valid_types:
            # Check if user explicitly asked for table
            query_lower = query.lower()
            if any(k in query_lower for k in ['table', 'list', 'raw data', 'show data']):
                return "table"
            
            # Default based on heuristics
            if len(result_df.columns) == 2:
                return "bar"
            
            # Smart heuristic: If we have numeric columns like 'price', 'sales', 'quantity', use bar
            cols_lower = [str(c).lower() for c in result_df.columns]
            if any(k in cols_lower for k in ['price', 'sales', 'quantity', 'amount', 'revenue', 'profit']):
                # Check if we have at least one numeric column (pandas check)
                numeric_cols = result_df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    return "bar"

            return "table"
        
        return viz_type
    
    def _clean_sql(self, sql: str) -> str:
        """Clean and validate SQL query using AST parsing"""
        # Remove markdown code blocks
        sql = sql.replace('```sql', '').replace('```', '').strip()
        
        # Remove any explanatory text before/after
        lines = sql.split('\n')
        sql_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('--'):
                sql_lines.append(line)
        
        sql = ' '.join(sql_lines)
        
        # Validate using AST parsing
        is_valid, error_msg = self.validate_sql_query(sql)
        if not is_valid:
            raise ValueError(error_msg)
        
        return sql
    
    def validate_sql_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate SQL query using AST parsing for security
        
        Args:
            query: SQL query to validate
            
        Returns:
            (is_valid, error_message)
        """
        try:
            # Parse the SQL query
            parsed = sqlparse.parse(query)
            
            if not parsed:
                return False, "Invalid SQL syntax: Unable to parse query"
            
            # Check for multiple statements (SQL injection prevention)
            if len(parsed) > 1:
                return False, "Multiple SQL statements detected. Only single SELECT queries are allowed"
            
            statement = parsed[0]
            
            # Get the statement type
            stmt_type = statement.get_type()
            
            # Only allow SELECT and WITH (CTE) statements
            if stmt_type not in ('SELECT', 'UNKNOWN'):  # UNKNOWN can be WITH clause
                return False, f"Only SELECT queries are allowed. Detected: {stmt_type}"
            
            # Check for destructive keywords in tokens
            dangerous_keywords = {
                'DROP', 'DELETE', 'TRUNCATE', 'UPDATE', 'INSERT', 'ALTER',
                'CREATE', 'REPLACE', 'EXEC', 'EXECUTE', 'CALL'
            }
            
            # Traverse all tokens
            for token in statement.flatten():
                if token.ttype is Keyword:
                    keyword_upper = token.value.upper()
                    if keyword_upper in dangerous_keywords:
                        return False, f"Unsafe SQL operation detected: {keyword_upper}. Only SELECT queries are allowed"
            
            # Check for system functions that could be dangerous
            query_upper = query.upper()
            dangerous_functions = ['LOAD_EXTENSION', 'ATTACH', 'DETACH', 'PRAGMA']
            for func in dangerous_functions:
                if func in query_upper:
                    return False, f"Unauthorized function detected: {func}"
            
            return True, None
            
        except Exception as e:
            return False, f"SQL validation error: {str(e)}"
