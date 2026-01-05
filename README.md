# Talk-to-Data AI 🤖

Enterprise-grade natural language to data querying system using LLM Agents. Upload any data format, ask questions in plain English, and get instant insights with beautiful visualizations.

## ✨ Features

- 🗂️ **Multi-Format Support**: CSV, Excel, JSON, SQL dumps, Parquet, and more
- 🧠 **AI-Powered Analysis**: Automatic data profiling with quality assessment and insights
- 💬 **Natural Language Queries**: Ask questions in plain English - no SQL knowledge needed
- 📊 **Smart Visualizations**: Auto-generated charts (bar, line, pie, scatter) and tables
- 💾 **Session Management**: Handle multiple datasets with isolated contexts
- ⚡ **Real-time Query Execution**: Powered by DuckDB for lightning-fast in-memory queries
- 🎨 **Modern UI**: Beautiful glassmorphism design with dark mode

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **Google Gemini**: LLM for natural language understanding
- **DuckDB**: In-memory SQL query engine
- **PostgreSQL**: Session and metadata storage
- **Pandas**: Data processing and analysis
- **SQLAlchemy**: ORM and database management

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe frontend development
- **Tailwind CSS**: Utility-first styling
- **Recharts**: Data visualization library
- **Zustand**: Lightweight state management

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL (or SQLite for simpler setup)
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Mahalakshmi4405/texttodata.git
cd texttodata
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

**Environment Configuration** (`.env`):
```env
DATABASE_URL=sqlite:///./talktodata.db  # Or use PostgreSQL
GEMINI_API_KEY=your_api_key_here
UPLOAD_DIR=./uploads
DEBUG=true
```

```bash
# Start the backend server
python main.py
```

Backend will run at `http://localhost:8000`

### 3. Frontend Setup

```bash
# From project root
npm install

# Start development server
npm run dev
```

Frontend will run at `http://localhost:3000`

## 📖 Usage Guide

### 1. Create a Session
- Click the "+" button in the header
- Enter a session name (e.g., "Sales Analysis 2024")

### 2. Upload Your Data
- Drag & drop or click to upload your data file
- Supported formats: CSV, Excel, JSON, SQL dumps, Parquet
- AI will automatically analyze your data and show insights

### 3. Ask Questions
Use the chat interface to query your data in natural language:
- "What is the total sales by region?"
- "Show me the top 10 products by revenue"
- "What is the average order value over time?"
- "Show me customers from California with orders > $1000"

### 4. View Results
- Results are automatically visualized (tables, charts)
- Click suggested queries to quickly explore your data
- SQL queries are shown for transparency

## 📂 Project Structure

```
texttodata/
├── backend/
│   ├── agents/
│   │   ├── llm_agent.py          # Gemini LLM integration
│   │   └── prompts.py            # Prompt engineering
│   ├── services/
│   │   ├── data_ingestor.py      # Multi-format data loading
│   │   ├── data_profiler.py      # Data analysis engine
│   │   ├── query_executor.py     # DuckDB query execution
│   │   └── session_manager.py    # Session CRUD operations
│   ├── models.py                 # SQLAlchemy models
│   ├── config.py                 # App configuration
│   └── main.py                   # FastAPI application
├── app/
│   ├── layout.tsx                # Next.js root layout
│   ├── page.tsx                  # Main dashboard
│   └── globals.css               # Global styles
├── components/
│   ├── DataUpload.tsx            # File upload component
│   ├── ChatInterface.tsx         # NL query interface
│   └── DataVisualization.tsx     # Charts and tables
└── lib/
    ├── api.ts                    # API client
    └── store.ts                  # State management
```

## 🎯 API Endpoints

| Endpoint                 | Method | Description         |
| ------------------------ | ------ | ------------------- |
| `/sessions`              | GET    | List all sessions   |
| `/sessions`              | POST   | Create new session  |
| `/sessions/{id}`         | GET    | Get session details |
| `/sessions/{id}`         | DELETE | Delete session      |
| `/upload`                | POST   | Upload data file    |
| `/query`                 | POST   | Execute NL query    |
| `/sessions/{id}/history` | GET    | Get query history   |

## 🧪 Example Queries

Once you've uploaded data, try these:

**Aggregations**
- "What is the total revenue?"
- "Show me the average price by category"

**Grouping**
- "Sales by product"
- "Count of orders by month"

**Top N**
- "Top 5 customers by spending"
- "Bottom 10 products by quantity"

**Filtering**
- "Show me all orders from 2024"
- "Products where price > 100"

**Time Series**
- "Revenue trend over time"
- "Daily sales for last month"

## 🔒 Security Notes

- SQL injection protection via LLM query validation
- Blocked destructive operations (DROP, DELETE, UPDATE)
- Session-based data isolation
- File upload size limits

## 🐛 Troubleshooting

**Backend won't start:**
- Check Python version: `python --version` (≥3.9 required)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Ensure `.env` file exists with GEMINI_API_KEY

**Frontend build errors:**
- Clear cache: `rm -rf .next node_modules package-lock.json`
- Reinstall: `npm install`

**Database errors:**
- For SQLite: Ensure write permissions in backend directory
- For PostgreSQL: Verify connection string in `.env`

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use this project for your own purposes!

## 🙏 Acknowledgments

- Google Gemini for natural language understanding
- DuckDB for blazing-fast query execution
- Next.js team for amazing developer experience

