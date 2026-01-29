# 🛡️ SentinalAI - Conflict Detection System

A real-time conflict detection and analysis web application for identifying escalating tensions in conversations.

## Features

✨ **2-Column Web Interface**

- **LEFT (Chat Section)**: Clean, scrollable message feed with color-coded severity
- **RIGHT (Analysis Panel)**: Real-time conflict scoring, detected flags, and AI suggestions
- **BOTTOM (Controls)**: User selector dropdown, message input, and send button

🎨 **Visual Indicators**

- **Green messages**: Low conflict (constructive tone)
- **Yellow messages**: Medium conflict (some tension detected)
- **Red messages**: High conflict (escalating language)

📊 **Conflict Analysis**

- Conflict score (0-100%)
- Risk level indicator with gradient meter
- Detected conflict flags
- AI-powered suggestions for de-escalation

👥 **Multi-User Support**

- Switch between Alice, Bob, and Manager personas
- Demo conversations pre-loaded
- No login required

## Architecture

- **Backend**: Flask REST API (`app.py`)
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **Analysis**: Rule-based conflict detection with extensible model integration

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

The app will start at `http://localhost:5000`

### 3. Open in Browser

Visit `http://localhost:5000` - no login needed!

## Usage

1. **Select a User**: Choose Alice, Bob, or Manager from the dropdown
2. **View Conversation**: Previous messages appear in the chat section
3. **Send Message**: Type in the input box and press Enter or click Send
4. **View Analysis**: Watch the conflict score, flags, and suggestions update in real-time

## Project Structure

```
SentinalAI/
├── app.py                 # Flask backend & API endpoints
├── model.py              # ML model integration (RoBERTa)
├── rules.py              # Rule-based conflict scoring
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Main web interface
└── static/
    ├── style.css         # Responsive styling
    └── script.js         # Frontend interactivity
```

## API Endpoints

- `GET /` - Main interface
- `GET /api/messages/<user>` - Get conversation for a user
- `POST /api/analyze` - Analyze text for conflict indicators
- `POST /api/send-message` - Send and analyze a new message

## Key Technologies

- **Framework**: Flask 2.3+
- **Frontend**: Vanilla JS (no framework dependencies)
- **Styling**: Pure CSS3 with gradients & animations
- **Analysis**: Keyword matching + rule-based scoring (extensible for ML models)

## Future Enhancements

- Integrate RoBERTa model from `model.py` for NLP-based detection
- Persistent message storage with database
- User authentication & session management
- Multi-language support
- Export analysis reports
- Real-time WebSocket updates

## Demo Personas

- **Alice**: Assertive communicator, sometimes aggressive
- **Bob**: Analytical, can be dismissive
- **Manager**: Mediator role, focuses on resolution

## License

MIT

---

**Note**: This is a demo application for conflict detection. Always prioritize human judgment in real conflict resolution scenarios.

Conflict detection and intervention system using RoBERTa and rule-based scoring.

## Project Structure

- **app.py** - Streamlit UI frontend for the conflict detection interface
- **model.py** - RoBERTa model inference for conflict detection
- **rules.py** - Conflict scoring logic and rule-based analysis
- **requirements.txt** - Python dependencies
- **.gitignore** - Git ignore rules

## Setup

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
streamlit run app.py
```

## Features

- Real-time conflict detection
- RoBERTa-based NLP inference
- Rule-based scoring system
- Streamlit web interface
