# 🧠 IntelligenceHUB v5.0

Sistema completo di gestione amministrazione per commesse, ticket e task.

## 🚀 Quick Start

### Prerequisiti
- PostgreSQL 15+
- Python 3.11+
- Node.js 18+
- npm/yarn

### Installazione

1. **Database Setup**
```bash
# Assicurati che PostgreSQL sia attivo con database 'intelligence'
sudo systemctl start postgresql
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

3. **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

### URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📊 Features Implementate

### ✅ Sistema Tipi Commesse
- CRUD completo con interfaccia Material-UI
- Validazione business logic
- Import/Export CSV
- Statistics e monitoring

### 🔧 Backend APIs
- FastAPI con documentazione automatica
- SQLAlchemy ORM con PostgreSQL
- Pydantic validation
- Authentication ready

### 🎨 Frontend React
- TypeScript + Material-UI
- Service layer per API calls
- Error handling e notifications
- Responsive design

## 🗃️ Database Schema

### Tabelle Principali
- `tipi_commesse` - Configurazione tipi commesse
- `milestones` - Milestone progetti (estesa)
- `modelli_task` - Template task riutilizzabili

### Relazioni
- TipoCommessa → Milestones (1:N)
- TipoCommessa → ModelliTask (1:N)
- Milestone → ModelliTask (1:N)

## 📁 Struttura Progetto

```
/var/www/intelligence/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routes/          # FastAPI routes
│   │   ├── services/        # Business logic
│   │   └── core/            # Configuration
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   └── types/           # TypeScript types
│   └── package.json
└── scripts/                 # Utility scripts
```

## 🧪 Testing

```bash
# Test sistema completo
./scripts/test_system.sh

# Test solo backend
cd backend && python -m pytest

# Test solo frontend  
cd frontend && npm test
```

## 🚀 Deployment

### Development
```bash
./scripts/start_backend.sh
./scripts/start_frontend.sh
```

### Production
```bash
# Backend
cd backend && gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app

# Frontend
cd frontend && npm run build
```

## 📞 Support

Per supporto tecnico e documentazione aggiuntiva:
- **Documentazione API**: http://localhost:8000/docs
- **Repository**: IntelligenceHUB v5.0
- **Autore**: Stefano Andrello & Claude AI Assistant
