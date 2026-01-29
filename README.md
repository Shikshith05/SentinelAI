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

## Setup

## Running on Another Laptop

### Prerequisites

- **Git**
- **Python 3.10+** (recommended)
- **Node.js 18+** and **npm**

### 1. Clone the Repository

```bash
git clone <YOUR_REPO_URL>
cd SentinalAI
```

### 2. Create & Activate a Python Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 5. Run the Backend

```bash
cd ..
uvicorn app:app --reload --port 8000
```

### 6. Run the Frontend (New Terminal)

```bash
cd frontend
npm run dev
```

The frontend runs at `http://localhost:3000` and connects to the API at `http://localhost:8000`.

### 1. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Backend

```bash
uvicorn app:app --reload --port 8000
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 4. Run the Frontend

```bash
npm run dev
```

The frontend runs at `http://localhost:3000` and connects to the API at `http://localhost:8000`.

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
