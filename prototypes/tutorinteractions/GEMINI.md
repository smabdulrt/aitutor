# AI Tutor - Gemini Integration

## Architecture Overview

The AI Tutor uses Gemini 2.0 Live API to power "Adam", an expert AI tutor that interacts with students through voice, video, and scratchpad.

### Core Components

1. **Gemini Live API**: Real-time streaming AI (text + audio + video)
2. **Teaching Assistant**: Proactive system that enhances Adam's teaching
3. **DashSystem**: Adaptive learning algorithm (DASH by Mozer & Lindsay)
4. **MediaMixer**: Combines camera, screen, and scratchpad feeds

## System Flow

```
Student ←→ Frontend (React) ←→ Gemini Live API ←→ Teaching Assistant
                ↓                                        ↓
           MediaMixer                            Vector DB + Knowledge Graph
```

## Development Status

### ✅ Completed Features
- Gemini Live API integration (text/audio streaming)
- Multi-modal input (camera, screen, scratchpad)
- DashSystem adaptive learning (K-12 Math)
- User profile management
- Question Generator Agent
- MediaMixer video combining

### 🚧 In Progress
- **Teaching Assistant System** (see: TEACHING_ASSISTANT_REQUIREMENTS.md)
  - Long-term memory (Vector DB + Knowledge Graph)
  - Emotional intelligence
  - Historical context provider
  - Performance tracking

### 📋 Backlog
- Curriculum Builder Agent (web scraping for new questions)
- Scale curriculum storage (one file per skill)
- Expand skills beyond K-12 Math

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Gemini API key

### Run the System

```bash
# 1. Start backend
python /path/to/venv/bin/python run_tutor.sh

# 2. Start MediaMixer
python MediaMixer/media_mixer.py

# 3. Start frontend
cd frontend
npm install
npm start
```

## Teaching Philosophy

Adam follows the Socratic method - never giving direct answers, always guiding students to discover solutions themselves. The Teaching Assistant enhances this by providing:

- Historical context from past sessions
- Emotional state awareness
- Performance insights
- Proactive engagement

## Next Steps

See `TEACHING_ASSISTANT_REQUIREMENTS.md` for detailed implementation plan of the Teaching Assistant system currently in development.
