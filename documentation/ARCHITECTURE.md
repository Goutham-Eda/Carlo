# Technical Architecture Document
# CARLO - Contract Analysis System

**Version**: 1.0  
**Date**: February 14, 2026  
**Status**: Draft  
**Owner**: Engineering Team

---

## 1. System Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│  (React Frontend - Web Application + Progressive Web App)      │
└────────────────────┬───────────────────────────┬────────────────┘
                     │                           │
                     │ REST API                  │ WebSocket
                     │                           │
┌────────────────────▼───────────────────────────▼────────────────┐
│                      API Gateway (FastAPI)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Auth Service │  │ Rate Limiter │  │ Load Balancer│         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────┬──────────────┬──────────────┬──────────────┬──────────┬─────────┘
         │              │              │              │          │
    ┌────▼────┐   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐  ┌──▼────┐
    │Document │   │Analysis │   │Financial│   │Renego-  │  │Negoti- │
    │ Service │   │ Service │   │Calculator   │tiation  │  │ation   │
    │         │   │         │   │         │   │ Engine  │  │ Bot    │
    │         │   │         │   │         │   │         │  │(Phase2)│
    └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘  └───┬────┘
         │              │              │              │          │
    ┌────▼──────────────▼──────────────▼──────────────▼──────────▼────┐
    │              AI Processing Layer                                 │
    │  ┌──────────────────────────────────────────────┐               │
    │  │     LangChain Document Processing Pipeline   │               │
    │  └──────────────────────────────────────────────┘               │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  ┌─────────┐│
    │  │  Claude AI   │  │   spaCy NER  │  │ Sentence │  │Conversation│
    │  │  (Anthropic) │  │   Pipeline   │  │Transform.│  │ Memory  ││
    │  └──────────────┘  └──────────────┘  └──────────┘  └─────────┘│
    └───────────────────────────┬──────────────────────────────────────┘
                                │
    ┌───────────────────────────▼───────────────────────────┐
    │                  Data Layer                           │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐   │
    │  │ PostgreSQL   │  │    Redis     │  │   S3     │   │
    │  │ (Contracts,  │  │  (Cache,     │  │  (PDF    │   │
    │  │  Analysis)   │  │   Sessions)  │  │ Storage) │   │
    │  └──────────────┘  └──────────────┘  └──────────┘   │
    └───────────────────────────────────────────────────────┘
```

### 1.2 Design Principles
- **Microservices**: Loosely coupled services for scalability
- **API-First**: Clean REST APIs for future integrations
- **Cloud-Native**: Designed for AWS/GCP deployment
- **AI-Augmented**: Humans in the loop for critical validations
- **Privacy-First**: Minimal data retention, encryption everywhere

---

## 2. Technology Stack

### 2.1 Frontend
```yaml
Framework: Next.js 14 (React 18)
Language: TypeScript
UI Library: Tailwind CSS + shadcn/ui
State Management: Zustand
Forms: React Hook Form + Zod validation
Charts: Recharts
File Upload: React Dropzone
PDF Viewer: react-pdf
Build Tool: Turbopack
Testing: Jest + React Testing Library + Playwright
```

### 2.2 Backend
```yaml
Framework: FastAPI 0.109+
Language: Python 3.11
API Documentation: OpenAPI (Swagger)
Authentication: JWT + OAuth2
Task Queue: Celery + Redis
Background Jobs: APScheduler
Validation: Pydantic v2
ORM: SQLAlchemy 2.0
Migration: Alembic
Testing: pytest + pytest-asyncio
```

### 2.3 AI/ML Stack
```yaml
LLM Provider: Anthropic Claude 3.5 Sonnet (primary)
LLM Orchestration: LangChain 0.1+
Document Processing: 
  - PyPDF2 / pdfplumber (text extraction)
  - pdf2image + Tesseract (OCR)
  - Unstructured.io (document chunking)
NER: spaCy 3.7 (en_core_web_lg)
Embeddings: sentence-transformers (all-MiniLM-L6-v2)
Classification: scikit-learn (for clause categorization)
Vector DB: Qdrant (for semantic search, future)
```

### 2.4 Database & Storage
```yaml
Primary DB: PostgreSQL 15
  - Schemas: contracts, users, analysis_results
Cache: Redis 7
  - Use: Session storage, rate limiting, job queue
Object Storage: AWS S3 / MinIO
  - Use: Uploaded PDFs, generated reports
```

### 2.5 Infrastructure
```yaml
Containerization: Docker + Docker Compose
Orchestration: Kubernetes (production) / Docker Compose (dev)
CI/CD: GitHub Actions
Cloud Provider: AWS (primary) / GCP (backup)
CDN: CloudFlare
Monitoring: 
  - Application: Sentry
  - Infrastructure: Datadog / Prometheus + Grafana
  - Logs: ELK Stack (Elasticsearch, Logstash, Kibana)
```

---

## 3. Core Components

### 3.1 Document Service

**Responsibility**: Handle document upload, storage, and text extraction

```python
# Pseudocode
class DocumentService:
    async def upload_document(file: UploadFile) -> Document:
        # 1. Validate file (type, size, malware scan)
        # 2. Store in S3
        # 3. Extract text (PDF → Text)
        # 4. OCR if needed (scanned PDF)
        # 5. Create document record in DB
        # 6. Trigger analysis job
        pass
    
    async def extract_text(pdf_path: str) -> str:
        # Try pdfplumber first (fast)
        # Fallback to OCR if low-quality
        pass
    
    async def detect_document_type(text: str) -> DocumentType:
        # Classify: Lease vs Loan vs Other
        # Use keyword matching + LLM
        pass
```

**Key Libraries**:
- `pdfplumber`: Text extraction
- `pdf2image` + `pytesseract`: OCR
- `boto3`: S3 storage
- `python-magic`: File type detection

---

### 3.2 Analysis Service

**Responsibility**: Parse contract, identify clauses, classify, assess risk

```python
class AnalysisService:
    async def analyze_contract(document_id: str) -> Analysis:
        # 1. Chunk document into clauses
        # 2. Classify each clause
        # 3. Extract entities (amounts, dates, rates)
        # 4. Calculate risk scores
        # 5. Generate summary
        pass
    
    async def segment_clauses(text: str) -> List[Clause]:
        # Use LangChain + Claude to identify clause boundaries
        # Return structured list of clauses
        pass
    
    async def classify_clause(clause: str) -> ClauseType:
        # Use few-shot prompting with Claude
        # Categories: PAYMENT, PENALTY, TERMINATION, etc.
        pass
    
    async def extract_entities(clause: str) -> Dict:
        # Use spaCy NER + custom patterns
        # Extract: MONEY, PERCENT, DATE, ORG
        pass
    
    async def calculate_risk_score(clause: Clause) -> int:
        # Rule-based + LLM assessment
        # Return 1-10 score
        pass
```

**AI Prompts** (examples):

```python
CLAUSE_SEGMENTATION_PROMPT = """
You are a legal document parser. Given a car lease/loan contract,
identify all distinct clauses and return them as a numbered list.

Contract:
{contract_text}

Return format:
1. [Clause 1 text]
2. [Clause 2 text]
...
"""

CLAUSE_CLASSIFICATION_PROMPT = """
Classify this contract clause into ONE of these categories:
- PAYMENT_TERMS: Interest rates, monthly payments, down payment
- PENALTY: Late fees, early termination, excess mileage
- INSURANCE: Required coverage, gap insurance
- MAINTENANCE: Service requirements, wear and tear
- TERMINATION: How to end the contract
- WARRANTY: Manufacturer warranty info
- MISCELLANEOUS: Other provisions

Clause: {clause_text}

Category:
"""

RISK_ASSESSMENT_PROMPT = """
Assess the risk of this clause on a scale of 1-10, where:
1-3 = Standard/Favorable
4-6 = Neutral
7-10 = Unfavorable/High Risk

Clause: {clause_text}
Category: {category}

Consider:
- Is it above market rates/fees?
- Does it limit consumer rights?
- Are there hidden costs?
- Is the language unusually restrictive?

Risk Score: [1-10]
Reasoning: [brief explanation]
"""
```

---

### 3.3 Financial Calculator Service

**Responsibility**: Calculate all financial metrics

```python
class FinancialCalculator:
    def calculate_emi(
        principal: float,
        annual_rate: float,
        tenure_months: int
    ) -> float:
        # EMI = [P x R x (1+R)^N] / [(1+R)^N-1]
        monthly_rate = annual_rate / 12 / 100
        emi = (principal * monthly_rate * 
               (1 + monthly_rate)**tenure_months) / \
              ((1 + monthly_rate)**tenure_months - 1)
        return round(emi, 2)
    
    def calculate_total_repayment(emi: float, tenure: int) -> float:
        return round(emi * tenure, 2)
    
    def calculate_total_interest(total: float, principal: float) -> float:
        return round(total - principal, 2)
    
    def generate_amortization_schedule(
        principal: float,
        rate: float,
        tenure: int
    ) -> List[AmortizationRow]:
        # Month-by-month breakdown
        schedule = []
        balance = principal
        for month in range(1, tenure + 1):
            interest = balance * (rate / 12 / 100)
            principal_paid = emi - interest
            balance -= principal_paid
            schedule.append({
                'month': month,
                'emi': emi,
                'principal': principal_paid,
                'interest': interest,
                'balance': max(0, balance)
            })
        return schedule
    
    def calculate_early_payoff_savings(
        current_month: int,
        remaining_balance: float,
        prepayment_penalty: float
    ) -> Dict:
        # Calculate savings if paid off early
        pass
```

**Validation**:
- All calculations must match Excel RATE/PMT functions
- Unit tests with known loan examples
- Rounding to 2 decimal places for currency

---

### 3.4 Renegotiation Engine

**Responsibility**: Generate actionable improvement recommendations

```python
class RenegotiationEngine:
    async def generate_recommendations(
        analysis: Analysis,
        market_data: MarketBenchmarks
    ) -> List[Recommendation]:
        # 1. Identify improvement opportunities
        # 2. Prioritize by savings potential
        # 3. Generate negotiation scripts
        pass
    
    async def benchmark_against_market(
        contract_terms: Dict,
        user_credit_score: int
    ) -> Comparison:
        # Compare user's APR vs market average
        # Compare fees vs typical fees
        # Identify outliers
        pass
    
    async def estimate_negotiation_success(
        recommendation: Recommendation
    ) -> float:
        # ML model trained on historical success rates
        # For MVP: rule-based heuristics
        pass
```

**Recommendation Examples**:

```python
recommendations = [
    {
        "type": "INTEREST_RATE_REDUCTION",
        "current": "8.5% APR",
        "target": "6.9% APR",
        "market_average": "7.2% APR (for credit score 720)",
        "potential_savings": "$2,340 over loan lifetime",
        "likelihood": "HIGH - Your credit score qualifies for better rates",
        "script": "Based on my credit score of 720, I've seen market rates..."
    },
    {
        "type": "FEE_REMOVAL",
        "item": "Dealer preparation fee",
        "amount": "$500",
        "rationale": "This fee is negotiable at most dealerships",
        "likelihood": "MEDIUM",
        "script": "I noticed the $500 prep fee. Since the car is already..."
    }
]
```

---

### 3.5 Negotiation Bot Service (Phase 2)

**Responsibility**: Provide real-time conversational AI support for contract negotiation

```python
class NegotiationBotService:
    def __init__(self):
        self.conversation_memory = {}  # Store conversation context per user
        
    async def chat(
        self,
        user_id: str,
        message: str,
        contract_analysis: Analysis
    ) -> ChatResponse:
        """
        Handle conversational interaction for negotiation guidance.
        
        Flow:
        1. Retrieve conversation history from memory
        2. Build context from contract analysis + user profile
        3. Generate contextual response using Claude
        4. Update conversation memory
        5. Return response with suggestions
        """
        
        # Get conversation history
        history = self.conversation_memory.get(user_id, [])
        
        # Build rich context
        context = self._build_context(contract_analysis, history)
        
        # Generate response
        response = await self._generate_response(message, context)
        
        # Update memory
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
        self.conversation_memory[user_id] = history[-20:]  # Keep last 20 exchanges
        
        return ChatResponse(
            message=response,
            suggestions=self._extract_suggestions(response),
            context_used=context
        )
    
    def _build_context(self, analysis: Analysis, history: List) -> Dict:
        """Build comprehensive context for AI response"""
        return {
            "contract_fairness_score": analysis.fairness_score,
            "weak_points": [
                c for c in analysis.clauses 
                if c.risk_score >= 7
            ],
            "market_comparison": {
                "user_apr": analysis.interest_rate,
                "market_apr": self._get_market_apr(analysis.credit_score),
                "difference": analysis.interest_rate - self._get_market_apr(analysis.credit_score)
            },
            "recommendations": analysis.recommendations,
            "conversation_history": history,
            "user_persona": "first-time buyer"  # Could be ML-inferred
        }
    
    async def _generate_response(self, message: str, context: Dict) -> str:
        """Generate contextual AI response using Claude"""
        
        prompt = f"""
        You are a knowledgeable car loan negotiation coach helping a user.
        
        User's Contract Details:
        - Fairness Score: {context['fairness_score']}/100
        - Current APR: {context['market_comparison']['user_apr']}%
        - Market Average APR: {context['market_comparison']['market_apr']}%
        - Weak Points: {', '.join([c.category for c in context['weak_points']])}
        
        Conversation History:
        {self._format_history(context['conversation_history'])}
        
        User's Question: {message}
        
        Provide specific, actionable advice. Include:
        1. Direct answer to their question
        2. Specific data/numbers to support your point
        3. Exact phrases they can use with the dealer
        4. What to expect as dealer response
        
        Keep response under 150 words, conversational tone.
        """
        
        response = await call_claude(prompt, max_tokens=300)
        return response
    
    async def role_play_mode(
        self,
        user_id: str,
        user_statement: str,
        contract_analysis: Analysis
    ) -> RolePlayResponse:
        """
        Simulate dealer responses for negotiation practice.
        AI plays the role of a car dealer.
        """
        
        dealer_response = await self._generate_dealer_response(
            user_statement,
            contract_analysis
        )
        
        # Also provide coaching feedback
        feedback = await self._generate_coaching_feedback(
            user_statement,
            dealer_response,
            contract_analysis
        )
        
        return RolePlayResponse(
            dealer_says=dealer_response,
            coach_feedback=feedback,
            suggested_next_move="Try asking about removing the prep fee as a compromise."
        )
    
    async def _generate_dealer_response(
        self,
        user_statement: str,
        analysis: Analysis
    ) -> str:
        """Generate realistic dealer objection/response"""
        
        prompt = f"""
        You are a car dealer. The customer just said:
        "{user_statement}"
        
        Their contract has:
        - APR: {analysis.interest_rate}%
        - Fairness Score: {analysis.fairness_score}/100
        
        Respond as a dealer would - be realistic, sometimes pushback,
        sometimes compromise. Keep under 100 words.
        """
        
        response = await call_claude(prompt, max_tokens=200)
        return response
```

**Key Features**:
- **Conversation Memory**: Maintains context across multiple messages
- **Context-Aware**: Uses contract analysis to provide personalized advice
- **Role-Play Mode**: Practice negotiation with AI playing dealer
- **Multi-Channel**: Can be deployed as web chat, WhatsApp bot, or SMS
- **Coaching Feedback**: Provides real-time feedback on user's negotiation approach

**Technology Stack**:
- **LLM**: Claude 3.5 Sonnet for conversational AI
- **Memory**: Redis for conversation state
- **Framework**: LangChain for conversation management
- **Channels**: 
  - Web: WebSocket for real-time chat
  - WhatsApp: Twilio Business API
  - SMS: Twilio Programmable SMS

---

## 4. Data Models

### 4.1 Database Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subscription_tier VARCHAR(20) DEFAULT 'free',
    credits_remaining INT DEFAULT 1
);

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    s3_key VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    document_type VARCHAR(50), -- 'lease', 'loan', 'unknown'
    processing_status VARCHAR(20), -- 'uploaded', 'processing', 'completed', 'failed'
    extracted_text TEXT,
    ocr_confidence FLOAT
);

-- Clauses table
CREATE TABLE clauses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    clause_number INT,
    clause_text TEXT NOT NULL,
    category VARCHAR(50), -- 'PAYMENT_TERMS', 'PENALTY', etc.
    risk_score INT CHECK (risk_score BETWEEN 1 AND 10),
    risk_explanation TEXT,
    page_number INT,
    extracted_entities JSONB -- {'amount': 500, 'currency': 'USD', ...}
);

-- Analysis results table
CREATE TABLE analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    overall_risk_score VARCHAR(20), -- 'LOW', 'MEDIUM', 'HIGH'
    contract_summary TEXT,
    
    -- Extracted financial terms
    principal_amount DECIMAL(12, 2),
    interest_rate DECIMAL(5, 2),
    tenure_months INT,
    monthly_payment DECIMAL(10, 2),
    down_payment DECIMAL(10, 2),
    
    -- Calculated values
    total_repayment DECIMAL(12, 2),
    total_interest DECIMAL(12, 2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recommendations table
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE,
    recommendation_type VARCHAR(50),
    current_value TEXT,
    recommended_value TEXT,
    potential_savings DECIMAL(10, 2),
    priority INT, -- 1=highest
    success_likelihood VARCHAR(20), -- 'HIGH', 'MEDIUM', 'LOW'
    negotiation_script TEXT
);

-- Audit log
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(100), -- 'upload_document', 'view_analysis', etc.
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    metadata JSONB
);
```

### 4.2 API Response Models (Pydantic)

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ClauseResponse(BaseModel):
    id: str
    clause_number: int
    text: str
    category: str
    risk_score: int
    risk_explanation: str
    entities: dict

class FinancialSummary(BaseModel):
    principal: float = Field(description="Loan amount")
    interest_rate: float = Field(description="Annual percentage rate")
    tenure_months: int
    monthly_payment: float
    total_repayment: float
    total_interest: float
    down_payment: Optional[float] = None

class Recommendation(BaseModel):
    type: str
    current_value: str
    recommended_value: str
    potential_savings: float
    likelihood: str  # HIGH, MEDIUM, LOW
    priority: int
    script: str

class AnalysisResponse(BaseModel):
    document_id: str
    status: str
    overall_risk: str  # LOW, MEDIUM, HIGH
    summary: str
    financial_summary: FinancialSummary
    clauses: List[ClauseResponse]
    recommendations: List[Recommendation]
    created_at: datetime
```

---

## 5. API Design

### 5.1 Core Endpoints

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh

POST   /api/v1/documents/upload
GET    /api/v1/documents/{document_id}
GET    /api/v1/documents/{document_id}/analysis
DELETE /api/v1/documents/{document_id}

GET    /api/v1/analysis/{analysis_id}
POST   /api/v1/analysis/{analysis_id}/export  # PDF report

GET    /api/v1/user/profile
GET    /api/v1/user/documents
PATCH  /api/v1/user/profile

POST   /api/v1/feedback  # User feedback on recommendations
```

### 5.2 Example API Flow

```http
### 1. Upload document
POST /api/v1/documents/upload
Authorization: Bearer {jwt_token}
Content-Type: multipart/form-data

file: [binary PDF data]

Response:
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "estimated_time_seconds": 25
}

### 2. Check processing status (WebSocket or polling)
GET /api/v1/documents/550e8400-e29b-41d4-a716-446655440000

Response:
{
  "document_id": "550e8400...",
  "status": "completed",
  "filename": "car_lease_contract.pdf",
  "document_type": "lease"
}

### 3. Get analysis results
GET /api/v1/documents/550e8400-e29b-41d4-a716-446655440000/analysis

Response:
{
  "document_id": "550e8400...",
  "overall_risk": "MEDIUM",
  "summary": "This is a 36-month closed-end lease for a 2024 Honda Accord...",
  "financial_summary": {
    "monthly_payment": 425.00,
    "down_payment": 2000.00,
    "total_payments": 15300.00,
    "disposition_fee": 395.00,
    "excess_mileage_fee": 0.25
  },
  "clauses": [
    {
      "id": "c1",
      "category": "PAYMENT_TERMS",
      "risk_score": 3,
      "text": "Monthly lease payment of $425.00...",
      "entities": {"amount": 425.00, "frequency": "monthly"}
    }
  ],
  "recommendations": [
    {
      "type": "EXCESS_MILEAGE_NEGOTIATION",
      "current_value": "$0.25/mile over 12,000 miles/year",
      "recommended_value": "Negotiate to $0.15/mile or 15,000 miles/year",
      "potential_savings": "$360/year if you drive 13,000 miles",
      "likelihood": "MEDIUM",
      "priority": 2,
      "script": "I typically drive about 13,000 miles per year..."
    }
  ]
}
```

---

## 6. Security Architecture

### 6.1 Authentication & Authorization

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ 1. Login (email/password)
       ▼
┌─────────────┐
│  API Gateway│
│   (FastAPI) │
└──────┬──────┘
       │ 2. Validate credentials
       │ 3. Generate JWT
       ▼
┌─────────────┐
│  Auth       │
│  Service    │
│             │
│ - bcrypt    │
│ - JWT RS256 │
└─────────────┘

JWT Payload:
{
  "sub": "user_id",
  "email": "user@example.com",
  "tier": "pro",
  "exp": 1234567890,
  "iat": 1234567890
}
```

**Security Measures**:
- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens signed with RS256
- Access tokens: 15-minute expiry
- Refresh tokens: 7-day expiry
- HTTPS only (TLS 1.3)
- CORS properly configured
- Rate limiting: 100 requests/minute per IP

### 6.2 Data Privacy

**PII Handling**:
- Minimal PII collection (email, name only)
- User can delete account + all data anytime
- Contracts auto-deleted after 30 days
- No sharing with third parties

**Document Security**:
- S3 buckets: private, encrypted at rest (AES-256)
- Pre-signed URLs for document access (expire in 1 hour)
- All API calls require authentication
- Audit logs for all document access

**Compliance**:
- GDPR: Right to access, delete, export data
- CCPA: Do not sell my personal information
- SOC 2 Type II (within 12 months)

### 6.3 Input Validation

```python
# All user inputs validated with Pydantic

class DocumentUploadRequest(BaseModel):
    # File validation handled by FastAPI
    file_size_max: int = 50 * 1024 * 1024  # 50 MB
    allowed_types: List[str] = ['application/pdf']

class ContractQuery(BaseModel):
    query: str = Field(max_length=500)
    
    @validator('query')
    def sanitize_query(cls, v):
        # Prevent SQL injection, XSS
        return bleach.clean(v)
```

**Protections**:
- SQL injection: Parameterized queries only (SQLAlchemy)
- XSS: All outputs sanitized
- CSRF: CSRF tokens for state-changing operations
- File upload: Virus scanning with ClamAV

---

## 7. Performance Optimization

### 7.1 Caching Strategy

```python
# Redis caching for expensive operations

# Cache analysis results (1 hour TTL)
@cache(key="analysis:{document_id}", ttl=3600)
async def get_analysis(document_id: str):
    return db.query(Analysis).filter_by(document_id=document_id).first()

# Cache market benchmarks (24 hours)
@cache(key="market_data:{credit_score_range}", ttl=86400)
async def get_market_benchmarks(credit_score: int):
    # Fetch from external API or database
    pass
```

### 7.2 Async Processing

```python
# Heavy processing done asynchronously

@celery_app.task
def process_document_task(document_id: str):
    """
    Background task for document analysis
    1. Extract text
    2. Segment clauses
    3. Classify & assess risk
    4. Calculate financials
    5. Generate recommendations
    6. Update database
    7. Send notification
    """
    document = db.get_document(document_id)
    
    # Step 1: Extract text
    text = extract_text_from_pdf(document.s3_key)
    
    # Step 2-5: Analysis (can parallelize)
    with ThreadPoolExecutor(max_workers=4) as executor:
        clauses_future = executor.submit(segment_and_classify, text)
        financial_future = executor.submit(extract_financial_terms, text)
        
        clauses = clauses_future.result()
        financial = financial_future.result()
    
    # Step 6: Save results
    analysis = Analysis(
        document_id=document_id,
        clauses=clauses,
        financial=financial,
        ...
    )
    db.save(analysis)
    
    # Step 7: Notify user (WebSocket or email)
    notify_user(document.user_id, "Analysis complete!")
```

### 7.3 Database Optimization

```sql
-- Indexes for common queries
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_status ON documents(processing_status);
CREATE INDEX idx_clauses_document_id ON clauses(document_id);
CREATE INDEX idx_analysis_document_id ON analysis_results(document_id);

-- Partial index for active documents
CREATE INDEX idx_active_documents 
ON documents(user_id, upload_date) 
WHERE processing_status = 'completed';
```

**Query Optimization**:
- Use select_related() / joinedload() for relationships
- Pagination for large result sets
- Database connection pooling (SQLAlchemy)

---

## 8. Deployment Architecture

### 8.1 AWS Deployment (Production)

```
┌─────────────────────────────────────────────────────────────┐
│                        CloudFront CDN                        │
│                  (Static assets, geo-caching)               │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  Application Load Balancer                  │
│          (SSL termination, health checks, autoscaling)      │
└────────┬───────────────────────────────┬────────────────────┘
         │                               │
    ┌────▼──────┐                   ┌────▼──────┐
    │   ECS     │                   │   ECS     │
    │ Frontend  │                   │  Backend  │
    │(Next.js)  │                   │ (FastAPI) │
    │           │                   │           │
    │ Fargate   │                   │ Fargate   │
    └───────────┘                   └─────┬─────┘
                                          │
                    ┌─────────────────────┼─────────────────┐
                    │                     │                 │
               ┌────▼────┐          ┌────▼────┐      ┌────▼────┐
               │   RDS   │          │ ElastiC │      │   S3    │
               │Postgres │          │  ache   │      │ Bucket  │
               │ (Multi- │          │ Redis   │      │ (PDFs)  │
               │   AZ)   │          └─────────┘      └─────────┘
               └─────────┘
```

**Autoscaling**:
- Frontend: 2-10 instances based on CPU/memory
- Backend: 3-20 instances based on request queue depth
- Database: Read replicas for analytics queries

**Monitoring**:
- CloudWatch for infrastructure metrics
- Sentry for error tracking
- X-Ray for distributed tracing
- Custom dashboards for business metrics

### 8.2 Cost Estimation (Monthly)

```
Compute (ECS Fargate):
  - Frontend: 2 x t3.small = $30
  - Backend: 3 x t3.medium = $90

Database (RDS):
  - PostgreSQL db.t3.medium (Multi-AZ) = $130

Cache (ElastiCache):
  - Redis cache.t3.micro = $15

Storage (S3):
  - 1TB documents = $23

AI API Costs (critical):
  - Claude API: 5000 analyses/month
  - Average 50k tokens per analysis
  - $3 per 1M input tokens = $750
  - (Optimize with caching, batching)

CDN (CloudFront):
  - 500GB transfer = $40

Total: ~$1,078/month (excluding AI)
With AI: ~$1,828/month

Revenue target: 100 paid users x $30 = $3,000
Margin: ~40%
```

---

## 9. Testing Strategy

### 9.1 Test Pyramid

```
         ┌───────────────┐
         │  E2E Tests    │  (10%)
         │  (Playwright) │
         └───────────────┘
        ┌─────────────────┐
        │ Integration Tests│  (30%)
        │   (pytest)       │
        └─────────────────┘
       ┌───────────────────┐
       │   Unit Tests      │  (60%)
       │   (pytest, Jest)  │
       └───────────────────┘
```

### 9.2 Critical Tests

```python
# Unit test: Financial calculator
def test_emi_calculation():
    principal = 25000
    rate = 7.5  # Annual rate
    tenure = 60  # months
    
    emi = FinancialCalculator.calculate_emi(principal, rate, tenure)
    
    assert emi == 500.76  # Verified with Excel PMT function
    assert emi > 0
    assert emi < principal  # Sanity check

# Integration test: Full analysis pipeline
@pytest.mark.asyncio
async def test_document_analysis_pipeline():
    # Upload test contract
    document = await upload_test_document("sample_lease.pdf")
    
    # Wait for processing
    analysis = await wait_for_analysis(document.id)
    
    # Assertions
    assert analysis.status == "completed"
    assert len(analysis.clauses) > 0
    assert analysis.overall_risk in ["LOW", "MEDIUM", "HIGH"]
    assert analysis.financial_summary.monthly_payment > 0
    assert len(analysis.recommendations) >= 3

# E2E test: User journey
@pytest.mark.e2e
def test_user_can_analyze_contract(page: Page):
    # Login
    page.goto("http://localhost:3000/login")
    page.fill("#email", "test@example.com")
    page.fill("#password", "testpass123")
    page.click("button[type=submit]")
    
    # Upload contract
    page.click("text=Analyze Contract")
    page.set_input_files("#file-upload", "tests/fixtures/sample_contract.pdf")
    
    # Wait for analysis
    page.wait_for_selector("text=Analysis Complete", timeout=30000)
    
    # Verify results displayed
    assert page.is_visible("text=Risk Score")
    assert page.is_visible("text=Financial Summary")
    assert page.is_visible("text=Recommendations")
```

---

## 10. Monitoring & Observability

### 10.1 Key Metrics

**Application Metrics**:
- Document processing time (P50, P95, P99)
- Analysis accuracy (validated against legal review)
- API response times
- Error rates by endpoint
- User satisfaction (NPS)

**Business Metrics**:
- Daily active users
- Contracts analyzed per day
- Conversion rate (free → paid)
- Average savings per contract
- Recommendation acceptance rate

**Infrastructure Metrics**:
- CPU/memory utilization
- Database query performance
- Cache hit rate
- API costs (Claude API usage)

### 10.2 Alerts

```yaml
# Example alert configuration

- name: High Error Rate
  condition: error_rate > 5% for 5 minutes
  severity: critical
  action: Page on-call engineer

- name: Slow Document Processing
  condition: p95_processing_time > 60 seconds
  severity: warning
  action: Slack notification

- name: AI API Budget Exceeded
  condition: daily_ai_cost > $100
  severity: warning
  action: Email finance team

- name: Database Connection Pool Exhausted
  condition: db_connections > 90% for 2 minutes
  severity: critical
  action: Auto-scale + page engineer
```

---

## 11. Future Enhancements

### Phase 2 (Months 4-6)
- Mobile apps (React Native)
- Contract comparison tool
- Browser extension for dealer websites
- Multi-language support

### Phase 3 (Months 7-12)
- Fine-tuned models on contract data
- Real-time chat with negotiation coach
- Integration with dealership systems (B2B)
- Blockchain-based contract verification (optional)

### Technical Debt Backlog
- Migrate to serverless (AWS Lambda) for cost optimization
- Implement vector DB for semantic search
- Build custom NER models for contracts
- GraphQL API for mobile apps

---

## 12. Open Technical Questions

1. **LLM Provider**: Claude vs GPT-4 vs open-source (cost vs quality)
2. **OCR Strategy**: Tesseract vs AWS Textract vs Google Vision (accuracy vs cost)
3. **Deployment**: ECS vs EKS vs Lambda (complexity vs flexibility)
4. **Clause Extraction**: Rule-based vs pure LLM (accuracy vs cost)
5. **Market Data**: Build crawler vs buy data feed (effort vs reliability)

---

**Document Owner**: Lead Engineer  
**Last Updated**: February 14, 2026  
**Next Review**: Weekly during development