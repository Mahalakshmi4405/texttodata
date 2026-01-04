# Talk-to-Data AI

Enterprise-grade natural language to SQL system using LLM Agents.

## 🚀 Features
- **Natural Language Querying**: Ask questions in plain English.
- **SQL Agent**: Automatically converts questions to SQL and executes them.
- **Visualization**: tabular data and charts.
- **Upload Data**: Support for Excel/CSV upload.

## 🛠️ Setup

### Prerequisites
- Python 3.9+
- OpenAI API Key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Mahalakshmi4405/texttodata.git
   cd texttodata
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the `backend` folder.
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=sk-proj-...
     ```

4. Initialize the database (optional, for sample data):
   ```bash
   python database.py
   ```

## ▶️ Running the Application

### Method 1: Streamlit UI
Run the interactive chat interface:
```bash
cd backend
streamlit run app.py
```

### Method 2: FastAPI Backend
Run the API server:
```bash
cd backend
uvicorn main:app --reload
```

## 📂 Project Structure
- `backend/`: Python source code
  - `agent.py`: LangChain SQL Agent logic
  - `app.py`: Streamlit frontend
  - `main.py`: FastAPI backend
  - `database.py`: Database initialization
