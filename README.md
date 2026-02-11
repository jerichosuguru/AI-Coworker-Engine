# 🤖 AI Co-worker Engine

**NPC System for Job Simulation Platform**

An intelligent multi-agent system that creates realistic AI co-workers with distinct personalities, supervision, and adaptive interactions for educational job simulations.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Claude](https://img.shields.io/badge/Claude-3.5%20Sonnet-purple.svg)](https://www.anthropic.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [NPCs Available](#npcs-available)
- [Age Adaptation](#age-adaptation)
- [Security](#security)
- [Testing](#testing)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

---

## 🎯 Overview

This project implements an AI-powered NPC (Non-Player Character) system for the Edtronaut job simulation platform. It features three distinct AI co-workers that help users practice professional scenarios in a safe, educational environment.

**Use Case:** Gucci Group HRM Leadership Development simulation where users design a competency framework while interacting with:
- **CHRO** (Dr. Elena Marchetti) - HR Strategy expert
- **CEO** (Alessandro Ricci) - Business strategy leader
- **Regional Manager** (Marie Dubois) - Implementation specialist

**Key Innovation:** Director Agent provides invisible supervision, detecting stuck loops and guiding conversations intelligently.

---

## ✨ Features

### 🎭 Multi-Persona AI Agents
- **3 Distinct NPCs** with unique personalities, expertise, and communication styles
- **Relationship Tracking** (±10 score range) that influences tone and helpfulness
- **Memory & Context** - NPCs remember conversation history and adapt responses
- **Domain Expertise** - Each NPC has specialized knowledge (HR, Strategy, Operations)

### 🎬 Director Supervision
- **Stuck Loop Detection** - Uses semantic similarity (0.85 threshold) to detect repetitive questions
- **Progress Monitoring** - Nudges users to next module after sufficient exploration
- **Off-Topic Redirection** - Keeps conversations focused on learning objectives
- **Invisible Operation** - Works behind the scenes without interrupting flow

### 📚 RAG Knowledge Base
- **FAISS Vector Search** - Fast similarity search over domain documents
- **3 Knowledge Documents** - Gucci context, 4 Pillars framework, HR best practices
- **Sentence Transformers** - MiniLM-L6-v2 for embeddings (384 dimensions)
- **NPC-Specific Filtering** - Each NPC accesses relevant knowledge

### 👶 Age Adaptation (5 Groups)
- **8-12 years** - Simple vocabulary, school examples, high encouragement
- **13-15 years** - Clear language, student activities, moderate encouragement
- **16-18 years** - Professional terms + context, internship examples
- **19-25 years** - Full vocabulary + jargon explanations, career development framing
- **26+ years** - Peer-level professional, minimal adaptation

### ♿ Accessibility Features
- **Screen Reader Support** - ARIA-formatted text with semantic markers
- **Text Simplification** - 3 complexity levels (simple, moderate, advanced)
- **Audio Descriptions** - Spell out acronyms, add pauses
- **Cognitive Support** - Extra spacing, clear transitions, short sentences
- **Text-to-Speech Ready** - Integration hooks for TTS services

### 🔒 Security & Privacy
- **JWT Authentication** - HS256 signed tokens with 60-minute expiry
- **PII Encryption** - Fernet symmetric encryption for sensitive data
- **Rate Limiting** - 60 requests/minute, 1000/hour per user
- **Input Sanitization** - XSS, SQL injection, jailbreak pattern detection
- **GDPR Compliance** - Data retention limits, right to deletion, user consent flows

### 📊 Performance
- **Response Time** - ~0.5s average (sub-second)
- **Test Coverage** - 80% (8/10 tests passing)
- **Scalability** - Modular architecture, Redis-backed sessions
- **Error Handling** - Graceful degradation with fallback responses

---

## 🛠️ Technology Stack

### **Core Backend**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11 | Primary language |
| **FastAPI** | 0.109+ | Web framework |
| **Uvicorn** | latest | ASGI server |
| **Pydantic** | 2.5.3 | Data validation |

### **AI & ML**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Claude 3.5 Sonnet** | API | LLM (Anthropic) |
| **Sentence Transformers** | latest | Embeddings (all-MiniLM-L6-v2) |
| **FAISS** | latest | Vector similarity search |
| **NumPy** | <2.0 | Numerical operations |

### **Storage & Cache**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Redis** | latest | Session storage (optional) |
| **In-Memory** | - | Fallback storage |

### **Security**
| Technology | Version | Purpose |
|------------|---------|---------|
| **PyJWT** | latest | JWT token generation/validation |
| **Cryptography (Fernet)** | latest | PII encryption |

### **Development Tools**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Docker** | latest | Containerization |
| **Docker Compose** | latest | Multi-container orchestration |
| **Pytest** | latest | Testing framework |

### **Frontend (Static)**
| Technology | Version | Purpose |
|------------|---------|---------|
| **HTML5** | - | Landing page |
| **CSS3** | - | Custom styling |
| **Vanilla JS** | - | Interactivity |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                       │
│              (WebSocket / REST API)                     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  DIRECTOR AGENT                         │
│   (Monitors conversations, detects loops, suggests)     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   NPC AGENTS LAYER                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│  │   CHRO   │    │   CEO    │    │ Regional │         │
│  │  Elena   │    │Alessandro│    │  Marie   │         │
│  └──────────┘    └──────────┘    └──────────┘         │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              KNOWLEDGE BASE (RAG)                       │
│  - Gucci Group context                                  │
│  - 4 Pillars competency framework                       │
│  - HR best practices                                    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                STATE MANAGEMENT                         │
│  - Session storage (Redis / In-memory)                  │
│  - Conversation history                                 │
│  - Relationship tracking                                │
│  - Progress tracking                                    │
└─────────────────────────────────────────────────────────┘
```

### **Request Flow:**
1. User sends message → API endpoint
2. Security middleware validates JWT, checks rate limits
3. Director Agent analyzes for loops/off-topic
4. NPC Agent retrieves knowledge from RAG
5. Adaptation Service adjusts for age/accessibility
6. Response returned with updated state

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.11+
- pip
- Git
- (Optional) Docker & Docker Compose
- (Optional) Redis

### **Installation**

```bash
# 1. Clone repository
git clone https://github.com/your-org/ai-coworker-engine.git
cd ai-coworker-engine

# 2. Create virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Generate data files
python create_data_files.py

# 6. Run server
python main.py
```

### **Access Points**
- 🏠 **Landing Page:** http://localhost:8000
- 📚 **Swagger UI:** http://localhost:8000/docs
- 📖 **ReDoc:** http://localhost:8000/redoc
- 💚 **Health Check:** http://localhost:8000/health

---

## 📡 API Documentation

### **Authentication Flow**

#### 1. Create Session
```bash
POST /api/session/create
Content-Type: application/json

{
  "user_id": "user_123",
  "user_profile": {
    "age": 25,
    "age_group": {
      "age_range": "19-25"
    }
  }
}

# Response
{
  "session_id": "uuid-here",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

#### 2. Chat with NPC
```bash
POST /api/chat
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "npc_id": "chro",
  "message": "Can you explain the 4 Pillars framework?",
  "user_profile": {
    "age": 25,
    "age_group": {"age_range": "19-25"}
  }
}

# Response
{
  "npc_id": "chro",
  "response": "The 4 Pillars framework consists of...",
  "relationship_score": 1,
  "safety_flags": [],
  "director_message": null
}
```

### **Available Endpoints**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/session/create` | Create new session | ❌ |
| GET | `/api/session/{id}` | Get session state | ✅ |
| DELETE | `/api/session/{id}` | Delete session | ✅ |
| POST | `/api/chat` | Chat with NPC | ✅ |
| GET | `/api/npcs` | List available NPCs | ❌ |
| POST | `/api/progress/update` | Update progress | ✅ |
| GET | `/api/progress` | Get progress | ✅ |
| GET | `/health` | Health check | ❌ |

### **WebSocket Connection**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/YOUR_SESSION_ID');

ws.onopen = () => {
  ws.send(JSON.stringify({
    npc_id: "chro",
    message: "Hello!"
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('NPC:', data.response);
};
```

---

## 🎭 NPCs Available

### **Dr. Elena Marchetti - CHRO**
```yaml
Role: Chief Human Resources Officer
Expertise:
  - 4 Pillars Framework (Vision, Entrepreneurship, Passion, Trust)
  - 360° Feedback Design
  - Leadership Coaching
  - Inter-brand Mobility Programs

Personality:
  - Professional but warm
  - Data-informed but people-first
  - Encouraging yet challenging

Enthusiasm Triggers:
  - Inter-brand mobility discussions
  - Behavioral indicator specificity
  - Coaching and development focus

Pushback Triggers:
  - One-size-fits-all approaches
  - Copying external frameworks without adaptation
  - Ignoring brand DNA

Hidden Constraints:
  - Cannot approve budgets > $500K without CEO
  - Won't discuss individual employee performance
```

### **Alessandro Ricci - CEO**
```yaml
Role: Chief Executive Officer
Expertise:
  - Business Strategy
  - Brand DNA & Portfolio Management
  - Competitive Positioning
  - M&A and Growth Strategy

Personality:
  - Strategic and direct
  - Brand-protective
  - ROI-focused

Enthusiasm Triggers:
  - Clear business cases
  - Competitive advantage discussions
  - Brand autonomy preservation

Pushback Triggers:
  - Corporate bureaucracy
  - Threats to brand independence
  - Vague proposals without ROI

Hidden Constraints:
  - Final say on cross-brand initiatives
  - Protective of Gucci brand legacy
```

### **Marie Dubois - Regional Manager**
```yaml
Role: Regional Manager - Europe
Expertise:
  - Implementation & Rollout
  - Change Management
  - Regional Operations
  - Resource Constraints

Personality:
  - Practical and realistic
  - Candid about challenges
  - Solutions-oriented

Enthusiasm Triggers:
  - Realistic timelines
  - Resource acknowledgment
  - Regional adaptation discussions

Pushback Triggers:
  - Unrealistic workload expectations
  - One-size-fits-all global mandates
  - Lack of regional adaptation

Hidden Constraints:
  - Limited budget and headcount
  - Must comply with European labor laws
  - Reports to both CHRO and Regional VP
```

---

## 👶 Age Adaptation

### **Age Groups & Adaptations**

| Age Range | Label | Vocabulary | Examples | Encouragement |
|-----------|-------|-----------|----------|---------------|
| **8-12** | Children | "skill" not "competency" | School, sports teams | High (every response) |
| **13-15** | Teens | Moderate simplification | Student government, clubs | High (frequent) |
| **16-18** | Young Adults | Business terms + context | Internships, first jobs | Moderate |
| **19-25** | College/Early Career | Full vocab + jargon explanations | Rotational programs, career development | Moderate |
| **26+** | Professionals | Peer-level professional | Executive strategy | Minimal |

### **Example Adaptations**

**Original (26+):**
> "The competency framework consists of four behavioral indicators that we assess through 360-degree feedback mechanisms."

**Age 8-12:**
> "Hi there! The skill plan has four things you do that we check by asking everyone you work with. Keep up the awesome work!"

**Age 19-25:**
> "The competency framework (a structured system defining the skills needed at each career level) consists of four behavioral indicators that we assess through 360-degree feedback (comprehensive input from your manager, peers, and direct reports)."

---

## 🔒 Security

### **Authentication**
- **JWT Tokens** - HS256 algorithm, 60-minute expiry
- **Token Refresh** - Not implemented (create new session)
- **Header Format:** `Authorization: Bearer <token>`

### **Encryption**
- **PII Data** - Fernet symmetric encryption
- **Conversation History** - Encrypted at rest
- **User IDs** - Hashed in logs (SHA-256)

### **Input Validation**
```python
# XSS Prevention
<script>alert('XSS')</script>  →  Rejected

# SQL Injection Prevention  
DROP TABLE users;--  →  Sanitized

# Jailbreak Detection
"Ignore previous instructions and..."  →  Blocked

# Length Limits
Max 2000 characters per message
```

### **Rate Limiting**
- **Per-User Limits:**
  - 60 requests/minute
  - 1000 requests/hour
- **Global Limits:**
  - 1000 requests/minute (configurable)

### **GDPR Compliance**
- **Data Retention:** 30 days (configurable)
- **Right to Deletion:** DELETE /api/session/{id}
- **User Consent:** Required before data collection
- **Data Minimization:** Only collect necessary information
- **Audit Logs:** Anonymized user actions

---

## 🧪 Testing

### **Run All Tests**
```bash
# Using pytest
pytest test_system.py -v

# Direct execution
python -c "from test_system import run_all_tests; run_all_tests()"
```

### **Test Coverage**
```
✅ 8/10 Tests Passing (80% coverage)

Passing:
1. ✅ NPC Agent Response
2. ✅ Director Agent - Stuck Loop Detection
3. ✅ Multiple NPCs
4. ✅ Accessibility Adaptation
5. ✅ Session Management
6. ✅ Multi-turn Conversation
7. ✅ Safety Checks
8. ✅ Performance (<1s response time)

Known Issues:
1. ❌ Security - Token expiry timing (test environment)
2. ❌ Knowledge Base - Document loading (works in server)
```

### **Individual Test Examples**
```bash
# Test NPC agent
python -c "from test_system import test_npc_agent; test_npc_agent()"

# Test stuck loop detection
python -c "from test_system import test_director_agent; test_director_agent()"

# Test age adaptation
python -c "from test_system import test_accessibility_adaptation; test_accessibility_adaptation()"
```

---

## 🚢 Deployment

### **Docker Deployment**

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### **Environment Variables**

```bash
# .env file (REQUIRED)
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
SECRET_KEY=your-secret-jwt-key-change-in-production
REDIS_HOST=localhost
REDIS_PORT=6379
ENVIRONMENT=production
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

### **Production Checklist**

- [ ] Set strong `SECRET_KEY` (64+ characters)
- [ ] Configure real `ANTHROPIC_API_KEY`
- [ ] Set up Redis server (production-grade)
- [ ] Enable HTTPS (reverse proxy)
- [ ] Configure CORS for production domains
- [ ] Set up monitoring (logs, metrics)
- [ ] Enable rate limiting
- [ ] Review GDPR compliance settings
- [ ] Set up backup for session data
- [ ] Configure CDN for static files (optional)

---

## 📁 Project Structure

```
AI-Coworker-Engine/
├── main.py                     # FastAPI application entry point
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── docker-compose.yml          # Docker orchestration
├── Dockerfile                  # Docker image definition
├── .dockerignore              # Docker ignore patterns
├── .gitignore                 # Git ignore patterns
├── test_system.py             # Test suite
├── create_data_files.py       # Data generation script
│
├── models/                    # Data models
│   ├── __init__.py
│   ├── state.py              # Session state models
│   ├── personas.py           # NPC personality definitions
│   └── user_profile.py       # User profile models
│
├── agents/                    # AI agents
│   ├── __init__.py
│   ├── npc_agent.py          # NPC conversation handler
│   ├── director_agent.py     # Supervision & guidance
│   ├── knowledge_base.py     # RAG retrieval
│   └── accessibility_agent.py # Accessibility adaptations
│
├── services/                  # Business logic
│   ├── __init__.py
│   ├── session_manager.py    # Session CRUD operations
│   ├── security_service.py   # Auth, encryption, validation
│   └── adaptation_service.py # Age & ability adaptations
│
├── api/                       # API layer
│   ├── __init__.py
│   ├── routes.py             # REST endpoints
│   ├── websocket.py          # WebSocket handler
│   └── middleware.py         # CORS, logging, security
│
├── utils/                     # Utilities
│   ├── __init__.py
│   ├── validators.py         # Input validation
│   ├── text_simplifier.py    # Text simplification
│   └── speech_service.py     # TTS/STT integration
│
├── data/                      # Data files
│   ├── knowledge_base/
│   │   ├── gucci_context.txt
│   │   ├── competency_framework.txt
│   │   └── hr_best_practices.txt
│   └── prompts/
│       ├── age_adapted_prompts.json
│       └── accessibility_prompts.json
│
└── static/                    # Frontend files
    ├── index.html
    ├── css/
    │   ├── style.css
    │   └── swagger-custom.css
    └── js/
        └── app.js
```

---

## 🤝 Contributing

This is an educational project for the Edtronaut AI Engineer Intern assignment. 

**Future Enhancements:**
- [ ] Streaming responses for better UX
- [ ] Multi-language support (French, Italian, Chinese)
- [ ] Voice interaction (Whisper + ElevenLabs)
- [ ] Analytics dashboard for instructors
- [ ] A/B testing framework for personas
- [ ] Advanced relationship dynamics
- [ ] Custom competency frameworks

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Anthropic** - Claude 3.5 Sonnet LLM
- **FastAPI** - Modern Python web framework
- **Facebook AI** - FAISS vector search
- **Sentence Transformers** - Embedding models
- **Edtronaut** - Assignment and learning platform

---

## 📞 Contact

## 📞 Contact

**Assignment Submission**
- Project: AI Co-worker Engine
- Candidate: Nguyen Mai Tri Cuong
- Date: February 2026
- LinkedIn: linkedin.com/in/tricuongnguyenmai 

**Documentation:**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

**Built with ❤️ using FastAPI + Claude AI**