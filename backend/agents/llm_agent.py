# LLM Agent with Dual Provider Support (Gemini + Ollama)

import google.generativeai as genai
import ollama
from config import get_settings
import pandas as pd
from typing import Dict, Optional, Tuple, List
import json
from agents.prompts import (
    SYSTEM_PROMPT, 
    QUERY_REFINEMENT_PROMPT, 
    INSIGHTS_GENERATION_PROMPT,
    VISUALIZATION_TYPE_PROMPT
)


class LLMAgent:
    """Dual-provider LLM agent supporting Google Gemini and local Ollama"""
    
    def __init__(self):
        settings = get_settings()
        self.provider = settings.llm_provider.lower()
        
        if self.provider == "gemini":
            genai.configure(api_key=settings.gemini_api_key)
            self.gemini_models = [
                'gemini-2.5-flash-lite',
                'gemini-flash-latest', 
                'gemini-2.5-flash'
            ]
            self.model = genai.GenerativeModel(self.gemini_models[0])
        
        elif self.provider == "ollama":
            self.ollama_base_url = settings.ollama_base_url
            self.ollama_model = settings.ollama_model
            self.available_models = self._get_ollama_models()
            
            # Auto-select model if configured one not available
            if self.ollama_model not in self.available_models and self.available_models:
                self.ollama_model = self.available_models[0]
                print(f"⚠️ Configured model not found. Using: {self.ollama_model}")
        
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}. Use 'gemini' or 'ollama'")
    
    def _get_ollama_models(self) -> List[str]:
        """Fetch available Ollama models"""
        try:
            models_response = ollama.list()
            models = [model['name'] for model in models_response.get('models', [])]
            if models:
                print(f"✅ Found {len(models)} Ollama models: {', '.join(models)}")
            return models
        except Exception as e:
            print(f"⚠️ Could not fetch Ollama models: {e}")
            return []
    
    def _generate_content(self, prompt: str, temperature: float = 0.2) -> str:
        """Universal content generation across providers"""
        if self.provider == "gemini":
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(temperature=temperature)
            )
            return response.text.strip()
        
        elif self.provider == "ollama":
            response = ollama.generate(
                model=self.ollama_model,
                prompt=prompt,
                options={'temperature': temperature}
            )
            return response['response'].strip()
    
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
        
        sql_query = self._generate_content(full_prompt, temperature=0.2)
        
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
        
        refined_query = self._generate_content(prompt, temperature=0.2)
        
        return self._clean_sql(refined_query)
    
    def generate_insights(
        self,
        profile: Dict,
        max_insights: int = 7
    ) -> str:
        """
        Generate natural language insights from data profile
        
        Args:
            profile: Data profile dictionary
            max_insights: Maximum number of insights
            
        Returns:
            Human-readable insights text
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
        
        insights_text = self._generate_content(prompt, temperature=0.3)
        
        # Clean markdown code blocks
        insights_text = insights_text.replace('```json', '').replace('```', '').strip()
        
        # Try to parse as JSON, fallback to raw text
        try:
            insights_list = json.loads(insights_text)
            if isinstance(insights_list, list):
                return "\n\n".join([f"• {insight}" for insight in insights_list[:max_insights]])
            else:
                return insights_text
        except:
            # If not JSON, return as is
            return insights_text
    
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
        
        viz_type = self._generate_content(prompt, temperature=0.1)
        
        # Validate
        valid_types = ['table', 'bar', 'line', 'pie', 'scatter', 'heatmap']
        if viz_type not in valid_types:
            # Default based on heuristics
            if len(result_df.columns) == 2:
                return "bar"
            return "table"
        
        return viz_type
    
    def _clean_sql(self, sql: str) -> str:
        """Clean and validate SQL query"""
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
        
        # Safety check - block destructive operations
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'UPDATE', 'INSERT', 'ALTER']
        sql_upper = sql.upper()
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                raise ValueError(f"Unsafe SQL operation detected: {keyword}")
        
        return sql
