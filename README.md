# BuildWise AI 🏢🤖

## Autonomous Multi-Agent Building Maintenance & Facility Management Platform

> **Enterprise-grade AI platform** that autonomously handles building maintenance through intelligent multi-agent collaboration — from complaint understanding to technician dispatch, cost estimation, and predictive failure detection.

---

## 🏗️ Architecture

```
buildwise-ai/
├── frontend/              # Next.js 15 + React 19 + TypeScript
│   ├── app/
│   │   ├── (auth)/        # Login, Register
│   │   └── (dashboard)/   # All dashboard pages
│   ├── components/        # Reusable UI components
│   └── lib/               # API client, Zustand store
│
├── backend/               # FastAPI + Python
│   ├── main.py            # App entry point
│   ├── config.py          # Settings
│   ├── database.py        # SQLAlchemy async engine
│   ├── models/            # 15 SQLAlchemy models
│   ├── routers/           # REST API endpoints
│   ├── services/          # AI, ML, CV, RAG services
│   └── agents/            # 10 AI agents
│
├── backend/ml/            # ML Pipeline
│   ├── train_models.py    # Training scripts
│   ├── sample_data_generator.py
│   └── models/            # Saved model artifacts
│
├── datasets/              # Sample data
├── docker-compose.yml     # Full stack deployment
└── .env.example           # Environment template
```

---

## 🤖 AI Multi-Agent System

| Agent | Role | Technology |
|-------|------|------------|
| 🎯 Coordinator | Orchestrates all agents | LangGraph |
| 🧠 Understanding | Extracts issue details | LLM + NLP |
| 🔍 Diagnosis | Technical diagnosis | LLM + Computer Vision |
| ⚡ Priority | Urgency classification | LLM + keyword rules |
| 📚 Knowledge | Retrieves repair procedures | RAG + ChromaDB |
| 👷 Technician AI | Recommends best technician | Scoring algorithm |
| 📅 Scheduling | Conflict-free scheduling | Constraint solver |
| 💰 Cost Estimator | Predicts repair costs | Rule + ML |
| 🔮 Predictive ML | Predicts equipment failures | XGBoost / LightGBM |
| 📊 Analytics | Updates KPIs & dashboards | Data aggregation |

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.11+

### 1. Clone & Configure
```bash
git clone https://github.com/your-org/buildwise-ai.git
cd buildwise-ai
cp .env.example .env
# Edit .env with your settings
```

### 2. Run with Docker Compose (Recommended)
```bash
docker-compose up -d
```

Services start at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **ChromaDB**: http://localhost:8001

### 3. Run Locally (Development)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 4. Train ML Models
```bash
cd backend
python ml/sample_data_generator.py
python ml/train_models.py
```

### 5. Pull Ollama Model (Optional)
```bash
docker exec buildwise_ollama ollama pull llama3.1
```

---

## 🔐 Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Super Admin | admin@buildwise.ai | demo123 |
| Facility Manager | manager@buildwise.ai | demo123 |
| Technician | tech@buildwise.ai | demo123 |
| Resident | resident@buildwise.ai | demo123 |

---

## 📡 API Reference

**Base URL**: `http://localhost:8000/api/v1`  
**Swagger Docs**: `http://localhost:8000/api/docs`

| Module | Endpoint | Methods |
|--------|----------|---------|
| Auth | `/auth/login`, `/auth/register`, `/auth/me` | POST, GET |
| Complaints | `/complaints` | GET, POST, PATCH, DELETE |
| Buildings | `/buildings` | GET, POST, DELETE |
| Technicians | `/technicians` | GET, POST, PATCH |
| Analytics | `/analytics/dashboard`, `/analytics/technician-performance` | GET |
| AI Agents | `/agents/run`, `/agents/rag-chat` | POST |
| Equipment | `/equipment` | GET, POST, PATCH |
| Predictions | `/predictions/run/{id}` | POST |
| Knowledge | `/knowledge/upload`, `/knowledge/chat` | POST |
| CV | `/cv/detect` | POST |

---

## 🏗️ Tech Stack

### Frontend
- **Next.js 15** + **React 19** + **TypeScript**
- **Tailwind CSS** (glassmorphism design system)
- **Framer Motion** (animations)
- **Recharts** (analytics charts)
- **React Flow** (agent workflow visualization)
- **Zustand** (state management)

### Backend
- **FastAPI** + **Python 3.11**
- **SQLAlchemy** (async ORM)
- **PostgreSQL** (database)
- **JWT Authentication** + RBAC

### AI / ML
- **LangGraph** (agent orchestration)
- **LangChain** (LLM integration)
- **ChromaDB** (vector store)
- **Sentence Transformers** (embeddings)
- **XGBoost** / **LightGBM** (failure prediction)
- **Isolation Forest** (anomaly detection)
- **YOLOv8** (computer vision)

### Infrastructure
- **Docker** + **Docker Compose**
- **Ollama** (local LLM)
- **OpenAI Compatible** API

---

## 🔧 Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql+asyncpg://...` |
| `JWT_SECRET_KEY` | JWT signing key | *required* |
| `OPENAI_API_KEY` | OpenAI API key | Optional |
| `OLLAMA_BASE_URL` | Ollama server | `http://localhost:11434` |
| `CHROMA_HOST` | ChromaDB host | `localhost` |
| `LLM_MODEL` | LLM model name | `gpt-4o-mini` |

---

## 🚢 Deployment

### Vercel (Frontend)
```bash
cd frontend
npx vercel --prod
```

### Render (Backend)
1. Connect GitHub repo
2. Set environment variables
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## 📊 User Roles

| Role | Capabilities |
|------|-------------|
| **Super Admin** | Full system access, user management |
| **Facility Manager** | Dashboard, complaints, technicians, analytics |
| **Technician** | Own tasks, upload completion photos |
| **Resident** | Submit complaints, track status |

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

Developed by Pravin raj TN & team.

---

<div align="center">
Built with ❤️ for intelligent building management<br/>
<strong>BuildWise AI</strong> — Making buildings smarter, one complaint at a time.
</div>
