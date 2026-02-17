
import os
import shutil
from pathlib import Path
from services.data_ingestor import DataIngestor
from services.data_profiler import DataProfiler
from agents.llm_agent import LLMAgent
from config import get_settings

# Setup
settings = get_settings()
ingestor = DataIngestor()
profiler = DataProfiler()
llm = LLMAgent()

file_path = "sales_data.xlsx"
if not os.path.exists(file_path):
    print(f"Error: {file_path} not found.")
    exit(1)

print(f"Testing upload for: {file_path}")

try:
    # 1. Ingest
    print("1. Ingesting data...")
    df, metadata = ingestor.ingest(file_path)
    print(f"   Success. Rows: {len(df)}")

    # 2. Profile
    print("2. Profiling data...")
    profile = profiler.profile(df)
    print("   Success. Profile keys: ", profile.keys())

    # 3. LLM Insights
    print("3. Generating Insights (this is likely where it fails)...")
    insights = llm.generate_insights(profile)
    print("   Success.")
    print("   Insights Preview:", insights[:100])

except Exception as e:
    print("\n" + "="*50)
    print("ERROR CAUGHT:")
    print("-" * 20)
    print(e)
    import traceback
    traceback.print_exc()
    print("="*50)
