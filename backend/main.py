# FastAPI Main Application

from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from typing import List, Optional, Dict
import shutil
import os
from pathlib import Path

from config import get_db, init_database, get_settings
from models import Session, DataSource, QueryHistory
from services.data_ingestor import DataIngestor
from services.data_profiler import DataProfiler
from services.query_executor import query_executor
from services.session_manager import session_manager
from agents.llm_agent import LLMAgent

# Initialize app
app = FastAPI(
    title="Talk-to-Data AI",
    description="Enterprise-grade natural language to data querying system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
settings = get_settings()
data_ingestor = DataIngestor()
data_profiler = DataProfiler()
llm_agent = LLMAgent()


# Pydantic models for requests/responses
class SessionCreate(BaseModel):
    name: str

class SessionResponse(BaseModel):
    id: int
    name: str
    created_at: str
    data_sources: List[Dict]
    
    class Config:
        from_attributes = True

class QueryRequest(BaseModel):
    session_id: int
    question: str

class QueryResponse(BaseModel):
    success: bool
    sql_query: Optional[str]
    result: Optional[List[Dict]]
    error: Optional[str]
    visualization_type: str
    execution_time_ms: float


# Routes

@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    init_database()
    print("Talk-to-Data AI Backend Ready!")

    # Check API Key
    key = settings.gemini_api_key
    if not key or not key.startswith("AIza"):
        print("\n" + "="*60)
        print("WARNING: Invalid or Missing Gemini API Key")
        print("The key must start with 'AIza'.")
        print("AI features will NOT work until you update backend/.env")
        print(f"Current key value (starts with): {key[:5] if key else 'None'}")
        print("="*60 + "\n")
    elif key == "AIzaSyCg-r2BugZzvOA-iXTpSb4JryI-wl5ltY4":
         print("\n" + "="*60)
         print("WARNING: You are using the default placeholder API Key.")
         print("Please update backend/.env with your own key.")
         print("="*60 + "\n")


@app.get("/")
async def root():
    return {
        "message": "Talk-to-Data AI API",
        "version": "1.0.0",
        "endpoints": {
            "sessions": "/sessions",
            "upload": "/upload",
            "query": "/query",
            "history": "/sessions/{session_id}/history"
        }
    }


@app.post("/sessions", response_model=SessionResponse)
async def create_session(
    session_create: SessionCreate,
    db: DBSession = Depends(get_db)
):
    """Create a new session"""
    session = session_manager.create_session(db, session_create.name)
    
    return SessionResponse(
        id=session.id,
        name=session.name,
        created_at=session.created_at.isoformat(),
        data_sources=[]
    )


@app.get("/sessions", response_model=List[SessionResponse])
async def list_sessions(db: DBSession = Depends(get_db)):
    """List all sessions"""
    sessions = session_manager.list_sessions(db)
    
    return [
        SessionResponse(
            id=s.id,
            name=s.name,
            created_at=s.created_at.isoformat(),
            data_sources=[
                {
                    "id": ds.id,
                    "name": ds.name,
                    "type": ds.source_type,
                    "row_count": ds.row_count
                }
                for ds in s.data_sources
            ]
        )
        for s in sessions
    ]


@app.get("/sessions/{session_id}")
async def get_session(session_id: int, db: DBSession = Depends(get_db)):
    """Get session details"""
    session = session_manager.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    data_sources = session_manager.get_data_sources(db, session_id)
    
    return {
        "id": session.id,
        "name": session.name,
        "created_at": session.created_at.isoformat(),
        "data_sources": [
            {
                "id": ds.id,
                "name": ds.name,
                "type": ds.source_type,
                "row_count": ds.row_count,
                "schema": ds.schema,
                "profile": {
                    "statistics": ds.data_profile.statistics,
                    "insights": ds.data_profile.insights,
                    "quality_score": ds.data_profile.data_quality_score,
                    "suggested_queries": ds.data_profile.suggested_queries
                } if ds.data_profile else None
            }
            for ds in data_sources
        ]
    }


@app.post("/upload")
async def upload_data(
    session_id: int = Form(...),
    file: UploadFile = File(...),
    db: DBSession = Depends(get_db)
):
    """Upload and ingest data file"""
    
    # Validate session
    session = session_manager.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Save file
    file_path = Path(settings.upload_dir) / f"session_{session_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Ingest data
        df, metadata = data_ingestor.ingest(str(file_path))
        
        # Get schema
        schema = data_ingestor.get_schema(df)
        
        # Add to database
        data_source = session_manager.add_data_source(
            db=db,
            session_id=session_id,
            name=file.filename,
            source_type=metadata['format'],
            file_path=str(file_path),
            schema=schema,
            row_count=len(df)
        )
        
        # Profile the data
        try:
            profile = data_profiler.profile(df)
            suggested_queries = data_profiler.generate_suggested_queries(df)
            
            # Generate insights using LLM (Handle errors gracefully)
            try:
                insights_text = llm_agent.generate_insights(profile)
            except Exception as llm_error:
                print(f"Warning: LLM generation failed: {llm_error}")
                insights_text = f"AI Insights unavailable. Error details: {str(llm_error)}\nPlease check your Google Gemini API Key in .env to enable AI features."
            
            # Save profile
            session_manager.add_data_profile(
                db=db,
                data_source_id=data_source.id,
                statistics=profile,
                insights=insights_text,
                quality_score=profile['data_quality']['overall_score'],
                suggested_queries=suggested_queries
            )
        except Exception as profile_error:
            print(f"Error generating/saving profile: {profile_error}")
            # We continue even if profile fails, so the data source is successfully linked
            # The UI will just show no profile (and thus no score 0/100)
        
        # Register in query executor
        query_executor.register_dataframe(session_id, df, table_name="data")
        
        return {
            "success": True,
            "data_source_id": data_source.id,
            "row_count": len(df),
            "columns": list(df.columns),
            "profile": {
                "insights": insights_text if 'insights_text' in locals() else None,
                "quality_score": profile['data_quality']['overall_score'] if 'profile' in locals() else 0,
                "suggested_queries": suggested_queries if 'suggested_queries' in locals() else []
            }
        }
    
    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def execute_query(
    query_request: QueryRequest,
    db: DBSession = Depends(get_db)
):
    """Execute natural language query"""
    
    session_id = query_request.session_id
    question = query_request.question
    
    # Get session
    session = session_manager.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get data sources
    data_sources = session_manager.get_data_sources(db, session_id)
    if not data_sources:
        raise HTTPException(status_code=400, detail="No data uploaded for this session")
    
    # Use first data source for now (enhance later for multi-source)
    ds = data_sources[0]
    schema = ds.schema
    
    # Load DataFrame
    df, _ = data_ingestor.ingest(ds.file_path)
    
    try:
        # Register in query executor (in case of restart)
        query_executor.register_dataframe(session_id, df, table_name="sales_data")  # Use a specific table name

        # Generate SQL
        sql_query = llm_agent.generate_sql(
            question=question,
            schema=schema,
            sample_data=df,
            table_name="sales_data"
        )
        
        # Execute query
        success, result_df, error, exec_time = query_executor.execute_query(session_id, sql_query)
        
        if not success:
            # Try to refine query
            refined_sql = llm_agent.refine_query(
                question=question,
                failed_query=sql_query,
                error_message=error,
                schema=schema,
                sample_data=df
            )
            
            success, result_df, error, exec_time = query_executor.execute_query(session_id, refined_sql)
            sql_query = refined_sql
        
        if success:
            # Suggest visualization
            viz_type = llm_agent.suggest_visualization(sql_query, result_df)
            
            # Convert result to dict
            result_records = result_df.to_dict(orient='records')
            
            # Save to history
            session_manager.add_query_history(
                db=db,
                session_id=session_id,
                nl_query=question,
                sql_query=sql_query,
                status="success",
                error_msg=None,
                result_summary={"row_count": len(result_df), "columns": list(result_df.columns)},
                viz_type=viz_type,
                exec_time_ms=exec_time
            )
            
            return QueryResponse(
                success=True,
                sql_query=sql_query,
                result=result_records,
                error=None,
                visualization_type=viz_type,
                execution_time_ms=exec_time
            )
        else:
            # Save error to history
            session_manager.add_query_history(
                db=db,
                session_id=session_id,
                nl_query=question,
                sql_query=sql_query,
                status="error",
                error_msg=error,
                result_summary={},
                viz_type="table",
                exec_time_ms=exec_time
            )
            
            return QueryResponse(
                success=False,
                sql_query=sql_query,
                result=None,
                error=error,
                visualization_type="table",
                execution_time_ms=exec_time
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions/{session_id}/history")
async def get_history(session_id: int, db: DBSession = Depends(get_db)):
    """Get query history for session"""
    history = session_manager.get_query_history(db, session_id)
    
    return [
        {
            "id": q.id,
            "question": q.natural_language_query,
            "sql": q.generated_sql,
            "status": q.execution_status,
            "error": q.error_message,
            "visualization_type": q.visualization_type,
            "execution_time_ms": q.execution_time_ms,
            "created_at": q.created_at.isoformat()
        }
        for q in history
    ]


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: int, db: DBSession = Depends(get_db)):
    """Delete session"""
    session_manager.delete_session(db, session_id)
    query_executor.close_session(session_id)
    
    return {"success": True, "message": "Session deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
