# CARLO Quick Start Guide
## Get Started in 15 Minutes

Welcome to the CARLO project! This guide will get you up and running quickly.

---

## ✅ Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.9+ installed (`python --version`)
- [ ] Node.js 16+ installed (`node --version`)
- [ ] PostgreSQL 13+ installed (`psql --version`)
- [ ] Git installed (`git --version`)
- [ ] Code editor (VS Code recommended)
- [ ] Anthropic API key ([get one here](https://console.anthropic.com))

---

## 🚀 Step-by-Step Setup (15 minutes)

### Step 1: Clone & Navigate (1 min)

```bash
# If using Git
git clone <your-repo-url>
cd carlo

# Or if starting fresh
mkdir carlo
cd carlo
```

### Step 2: Backend Setup (5 min)

```bash
# Create backend directory
mkdir -p src/backend
cd src/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic pydantic
pip install python-multipart python-jose[cryptography] passlib[bcrypt]
pip install anthropic openai langchain langchain-anthropic
pip install pdfplumber pdf2image pytesseract pillow
pip install pytest pytest-asyncio pytest-cov python-dotenv
pip install redis celery

# Save dependencies
pip freeze > requirements.txt
```

### Step 3: Create .env File (2 min)

```bash
# Create .env file in src/backend/
cat > .env << EOF
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/carlo_dev

# API Keys
ANTHROPIC_API_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_key_here  # Optional

# Security
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Storage
S3_BUCKET=carlo-documents-dev
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# Redis
REDIS_URL=redis://localhost:6379/0

# Environment
ENVIRONMENT=development
DEBUG=True
EOF

# IMPORTANT: Replace placeholders with real values!
```

### Step 4: Database Setup (3 min)

```bash
# Create database
createdb carlo_dev

# Or using psql:
# psql -U postgres
# CREATE DATABASE carlo_dev;

# Initialize Alembic
cd src/backend
alembic init alembic

# The initial migration will be created later
```

### Step 5: Frontend Setup (3 min)

```bash
# Navigate to src directory
cd ../../src

# Create Next.js app
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir --import-alias "@/*"

cd frontend

# Install additional dependencies
npm install zustand react-hook-form zod
npm install react-dropzone react-pdf
npm install recharts
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install lucide-react

# Development dependencies
npm install --save-dev @playwright/test
```

### Step 6: Verify Installation (1 min)

```bash
# Test Python
python --version  # Should be 3.9+

# Test Node
node --version  # Should be 16+

# Test database connection
psql -U postgres -d carlo_dev -c "SELECT version();"

# Test API key (optional - replace with your key)
echo "Testing Anthropic API..."
python -c "
from anthropic import Anthropic
import os
os.environ['ANTHROPIC_API_KEY'] = 'your-key-here'
client = Anthropic()
response = client.messages.create(
    model='claude-3-5-sonnet-20250514',
    max_tokens=50,
    messages=[{'role': 'user', 'content': 'Say hello!'}]
)
print(response.content[0].text)
"
```

---

## 🏃‍♂️ Running the Application

### Terminal 1: Start Backend

```bash
cd src/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload --port 8000

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete.
```

### Terminal 2: Start Frontend

```bash
cd src/frontend
npm run dev

# You should see:
#   ▲ Next.js 14.x.x
#   - Local:        http://localhost:3000
```

### Test It!

Open your browser to:
- Frontend: http://localhost:3000
- Backend API Docs: http://localhost:8000/docs

---

## 📁 Project Structure After Setup

```
carlo/
├── README.md
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   └── IMPLEMENTATION_ROADMAP.md
├── src/
│   ├── backend/
│   │   ├── venv/
│   │   ├── .env
│   │   ├── requirements.txt
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── database.py                # Database config
│   │   ├── models.py                  # SQLAlchemy models
│   │   ├── schemas.py                 # Pydantic schemas
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                # Authentication endpoints
│   │   │   ├── documents.py           # Document upload/management
│   │   │   └── analysis.py            # Analysis endpoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── document_extractor.py  # PDF text extraction
│   │   │   ├── clause_analyzer.py     # Clause segmentation/classification
│   │   │   ├── financial_calculator.py
│   │   │   └── recommendation_engine.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── ai_client.py           # Claude API wrapper
│   │   │   └── storage.py             # S3 or local storage
│   │   ├── alembic/                   # Database migrations
│   │   └── tests/
│   └── frontend/
│       ├── src/
│       │   ├── app/
│       │   │   ├── layout.tsx
│       │   │   ├── page.tsx           # Home page
│       │   │   ├── login/
│       │   │   ├── upload/
│       │   │   └── analysis/[id]/
│       │   ├── components/
│       │   │   ├── FileUpload.tsx
│       │   │   ├── Dashboard.tsx
│       │   │   ├── ClauseViewer.tsx
│       │   │   └── RecommendationCard.tsx
│       │   └── lib/
│       │       ├── api.ts              # API client
│       │       └── types.ts           # TypeScript types
│       ├── package.json
│       └── next.config.js
├── data/
│   └── sample_contracts/              # Test PDFs
├── tests/
└── scripts/
```

---

## 🎯 Your First Task: Create "Hello World" API

Let's verify everything works by creating a simple endpoint.

### 1. Create main.py

```python
# src/backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CARLO API",
    description="Contract Analysis, Review, and Loan Optimization",
    version="0.1.0"
)

# CORS configuration for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to CARLO API",
        "version": "0.1.0",
        "status": "healthy"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Test Claude AI integration
@app.get("/test-ai")
async def test_ai():
    from anthropic import Anthropic
    import os
    
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20250514",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": "Say 'CARLO is ready!' and give one fun fact about car loans."
        }]
    )
    
    return {
        "status": "success",
        "response": message.content[0].text
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2. Test It!

```bash
# Start the server
cd src/backend
source venv/bin/activate
python main.py

# In another terminal, test the endpoints:
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/test-ai

# Or open in browser:
# http://localhost:8000/docs  (Swagger UI)
```

---

## 🧪 Run Your First Test

```python
# src/backend/tests/test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to CARLO API"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

```bash
# Run tests
pytest tests/test_main.py -v
```

---

## 📋 Next Steps (After Setup Complete)

### Week 1 Tasks:
1. ✅ Complete setup (you just did this!)
2. ⬜ Create database models (User, Document, Clause)
3. ⬜ Set up Alembic migrations
4. ⬜ Create document upload endpoint
5. ⬜ Implement PDF text extraction
6. ⬜ Test with sample PDF

### Your Immediate TODO:
```bash
# 1. Replace placeholder values in .env
# 2. Create first database migration
# 3. Follow Week 1 tasks in IMPLEMENTATION_ROADMAP.md
```

---

## 🆘 Troubleshooting

### Common Issues:

**Python import errors**
```bash
# Make sure virtual environment is activated
which python  # Should point to venv/bin/python
pip list  # Verify packages installed
```

**Database connection failed**
```bash
# Check if PostgreSQL is running
pg_isready
# or
sudo service postgresql status  # Linux
brew services list  # Mac

# Test connection
psql -U postgres -d carlo_dev
```

**Port already in use**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # Mac/Linux
# Or change port in uvicorn.run()
```

**Anthropic API error**
```bash
# Verify API key is set
echo $ANTHROPIC_API_KEY

# Test API key
python -c "from anthropic import Anthropic; print(Anthropic().messages.create(model='claude-3-5-sonnet-20250514', max_tokens=10, messages=[{'role':'user','content':'hi'}]))"
```

---

## 📚 Helpful Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Anthropic API Docs](https://docs.anthropic.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

---

## 💡 Tips for Success

1. **Start Small**: Build one feature at a time
2. **Test Early**: Write tests as you go
3. **Document**: Comment your code, it'll save time later
4. **Use AI**: Claude can help debug and write code
5. **Ask for Help**: Use GitHub Issues or discussions

---

## 🎓 Learning Path

If you're new to any of these technologies:

1. **FastAPI** (2-3 hours): [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
2. **React/Next.js** (4-5 hours): [Next.js Learn](https://nextjs.org/learn)
3. **SQLAlchemy** (2 hours): [SQLAlchemy Core Tutorial](https://docs.sqlalchemy.org/en/20/core/tutorial.html)
4. **LangChain** (2 hours): [LangChain Quickstart](https://python.langchain.com/docs/get_started/quickstart)

---

**Setup Time**: ~15 minutes  
**First Feature**: ~1 week  
**MVP**: ~12 weeks

🚀 **You're ready to start building! Begin with Week 1 tasks in the Implementation Roadmap.**

Questions? Create an issue or ask Claude for help!

---

Last Updated: February 14, 2026
