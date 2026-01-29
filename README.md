# 🛡️ SentinalAI - Conflict Detection System

A real-time conflict detection and analysis web application for identifying escalating tensions in conversations.

## Architecture

- **Backend**: FastAPI (`app.py`)
- **Frontend**: Next.js + Tailwind CSS (`frontend/`)
- **Analysis**: Rule-based conflict detection with extensible model integration

## Features

- 2-column UI with chat and analysis panels
- Conflict score (0-100%) and risk level highlights
- Detected conflict indicators and AI suggestions
- Multi-user demo personas (Alice, Bob, Manager)

## Quick Start (Single Command)

To run the entire project with one command:

```bash
cd /path/to/SentinalAI
./run.sh
```

This will:

- Clean up ports 3000 and 8000
- Start the FastAPI backend on port 8000
- Start the Next.js frontend on port 3000
- Display both URLs and log file locations

## Setup

### Prerequisites

- **Git**
- **Python 3.10+** (recommended)
- **Node.js 18+** and **npm**

### Initial Setup

1. **Clone the Repository**

   ```bash
   git clone <YOUR_REPO_URL>
   cd SentinalAI
   ```

2. **Create & Activate a Python Virtual Environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Backend Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Running the Project

#### Option 1: Single Command (Recommended)

```bash
./run.sh
```

#### Option 2: Manual (Two Terminals)

Terminal 1 - Backend:

```bash
python -m uvicorn app:app --reload --port 8000
```

Terminal 2 - Frontend:

```bash
cd frontend
npm run dev
```

**Access the application:**

- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8000

## API Endpoints

- `GET /health` - Health check
- `GET /api/users` - List demo users
- `GET /api/messages/{user}` - Get conversation for a user
- `POST /api/analyze` - Analyze text for conflict indicators
- `POST /api/send-message` - Send and analyze a new message

## Project Structure

```
SentinalAI/
├── app.py                 # FastAPI backend & API endpoints
├── model.py               # ML model integration (RoBERTa)
├── rules.py               # Rule-based conflict scoring
├── requirements.txt       # Python dependencies
└── frontend/              # Next.js + Tailwind UI
```

## Notes

- The demo data is stored in-memory; restarting the backend resets conversations.
- If transformer models are unavailable, the backend falls back to a lightweight heuristic.
