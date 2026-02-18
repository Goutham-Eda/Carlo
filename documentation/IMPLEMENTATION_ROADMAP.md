# Implementation Roadmap
# CARLO Project - 12-Week MVP Development Plan

**Start Date**: February 17, 2026  
**MVP Launch Target**: May 12, 2026  
**Team Size**: 1-2 developers (can be solo with AI assistance)

---

## 🎯 Project Phases Overview

```
Phase 1: Foundation (Weeks 1-2)    ████████░░░░░░░░░░░░
Phase 2: Core Engine (Weeks 3-6)   ░░░░░░░░████████████
Phase 3: User Interface (Weeks 7-8) ░░░░░░░░░░░░░░░░████
Phase 4: Polish & Test (Weeks 9-11) ░░░░░░░░░░░░░░░░░░░░
Phase 5: Launch Prep (Week 12)     ░░░░░░░░░░░░░░░░░░░░██
```

---

## 📅 WEEK 1: Project Setup & Infrastructure

### Goals
- Set up development environment
- Initialize repositories
- Deploy basic infrastructure
- Validate AI API access

### Tasks

#### Day 1-2: Repository & Environment
- [ ] Create GitHub repository
- [ ] Set up branch protection (main, develop)
- [ ] Initialize pre-commit hooks (black, flake8, mypy)
- [ ] Create `.env.example` with required variables
- [ ] Set up local development environment
  ```bash
  # Backend
  python -m venv venv
  pip install fastapi uvicorn sqlalchemy alembic pydantic
  pip install langchain anthropic openai
  pip install pdfplumber pdf2image pytesseract
  pip install pytest pytest-asyncio pytest-cov
  
  # Frontend
  npx create-next-app@latest carlo-frontend --typescript --tailwind
  cd carlo-frontend
  npm install zustand react-hook-form zod recharts
  npm install react-dropzone react-pdf
  ```

#### Day 3-4: Database Setup
- [ ] Design initial database schema
- [ ] Create PostgreSQL database locally
- [ ] Set up Alembic migrations
- [ ] Create initial migration (users, documents, clauses tables)
- [ ] Test database connection
  ```python
  # alembic/versions/001_initial_schema.py
  def upgrade():
      op.create_table('users', ...)
      op.create_table('documents', ...)
      op.create_table('clauses', ...)
  ```

#### Day 5: AI API Integration
- [ ] Get Anthropic API key (claude.ai or console)
- [ ] Test basic Claude API call
- [ ] Implement retry logic and error handling
- [ ] Set up token usage tracking
  ```python
  # Test script
  from anthropic import Anthropic
  
  client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
  message = client.messages.create(
      model="claude-3-5-sonnet-20250514",
      max_tokens=1000,
      messages=[{"role": "user", "content": "Hello, Claude!"}]
  )
  print(message.content)
  ```

#### Day 6-7: CI/CD Pipeline
- [ ] Set up GitHub Actions
- [ ] Configure pytest to run on pull requests
- [ ] Set up code coverage reporting
- [ ] Create Docker Compose for local development
  ```yaml
  # docker-compose.yml
  version: '3.8'
  services:
    db:
      image: postgres:15
      environment:
        POSTGRES_DB: carlo_dev
        POSTGRES_PASSWORD: dev_password
    redis:
      image: redis:7-alpine
    backend:
      build: ./backend
      ports:
        - "8000:8000"
      depends_on:
        - db
        - redis
  ```

### Deliverables
- ✅ Working dev environment
- ✅ Database schema deployed locally
- ✅ Successful AI API test
- ✅ Basic CI/CD running

---

## 📅 WEEK 2: Document Processing Pipeline

### Goals
- Implement PDF upload and storage
- Build text extraction (PDF → text)
- Create document processing service

### Tasks

#### Day 1-2: File Upload API
- [ ] Create FastAPI endpoint for file upload
- [ ] Implement file validation (type, size, virus scan)
- [ ] Set up local file storage (for dev) / S3 (for prod)
- [ ] Create document database record
  ```python
  # app/api/documents.py
  @router.post("/upload")
  async def upload_document(
      file: UploadFile = File(...),
      current_user: User = Depends(get_current_user)
  ):
      # Validate file
      if file.content_type != "application/pdf":
          raise HTTPException(400, "Only PDF files allowed")
      
      # Save to S3 or local
      file_key = await storage.save_file(file)
      
      # Create DB record
      document = Document(
          user_id=current_user.id,
          filename=file.filename,
          s3_key=file_key,
          status="uploaded"
      )
      db.add(document)
      db.commit()
      
      return {"document_id": document.id, "status": "uploaded"}
  ```

#### Day 3-4: Text Extraction
- [ ] Implement PDF text extraction with pdfplumber
- [ ] Add OCR fallback for scanned PDFs (Tesseract)
- [ ] Handle multi-column layouts
- [ ] Clean extracted text (remove headers, footers)
  ```python
  # app/services/extractor.py
  def extract_text_from_pdf(pdf_path: str) -> str:
      text = ""
      
      try:
          # Try pdfplumber first (fast, accurate for digital PDFs)
          with pdfplumber.open(pdf_path) as pdf:
              for page in pdf.pages:
                  text += page.extract_text() or ""
          
          # If no text extracted, use OCR
          if len(text.strip()) < 100:
              text = ocr_pdf(pdf_path)
      
      except Exception as e:
          logger.error(f"Text extraction failed: {e}")
          raise
      
      return clean_text(text)
  
  def ocr_pdf(pdf_path: str) -> str:
      images = pdf2image.convert_from_path(pdf_path)
      text = ""
      for img in images:
          text += pytesseract.image_to_string(img)
      return text
  ```

#### Day 5-6: Document Type Detection
- [ ] Build classifier for lease vs loan
- [ ] Use keyword matching + LLM
- [ ] Extract basic metadata (parties, dates)
  ```python
  async def detect_document_type(text: str) -> str:
      # Keywords for quick classification
      lease_keywords = ['lessor', 'lessee', 'residual value', 'disposition fee']
      loan_keywords = ['borrower', 'lender', 'amortization', 'principal']
      
      # Count keyword matches
      lease_score = sum(1 for kw in lease_keywords if kw in text.lower())
      loan_score = sum(1 for kw in loan_keywords if kw in text.lower())
      
      # If unclear, ask Claude
      if abs(lease_score - loan_score) < 2:
          response = await claude_classify(text)
          return response.type
      
      return "lease" if lease_score > loan_score else "loan"
  ```

#### Day 7: Testing & Integration
- [ ] Write unit tests for text extraction
- [ ] Test with 10+ sample PDFs (various formats)
- [ ] Measure extraction accuracy
- [ ] Document edge cases

### Deliverables
- ✅ Working file upload API
- ✅ Text extraction with >95% accuracy
- ✅ Document type detection
- ✅ Test suite passing

---

## 📅 WEEK 3-4: Clause Segmentation & Classification

### Goals
- Segment contract into individual clauses
- Classify each clause by type
- Extract entities (amounts, dates, rates)

### Week 3 Tasks

#### Day 1-3: Clause Segmentation
- [ ] Design prompt for clause identification
- [ ] Implement LangChain document splitter
- [ ] Use Claude to segment text into clauses
- [ ] Validate segmentation quality
  ```python
  # app/services/clause_segmenter.py
  from langchain.text_splitter import RecursiveCharacterTextSplitter
  from anthropic import Anthropic
  
  SEGMENTATION_PROMPT = """
  You are analyzing a car lease/loan contract. Identify all distinct contractual clauses.
  
  Rules:
  - Each clause should be a complete, self-contained provision
  - Include section numbers if present
  - Separate payment terms, penalties, termination conditions, etc.
  
  Contract text:
  {text}
  
  Return as JSON:
  {{
    "clauses": [
      {{"number": 1, "text": "...", "title": "..."}},
      ...
    ]
  }}
  """
  
  async def segment_clauses(contract_text: str) -> List[Clause]:
      client = Anthropic()
      
      response = client.messages.create(
          model="claude-3-5-sonnet-20250514",
          max_tokens=4000,
          messages=[{
              "role": "user",
              "content": SEGMENTATION_PROMPT.format(text=contract_text)
          }]
      )
      
      clauses_json = json.loads(response.content[0].text)
      return [Clause(**c) for c in clauses_json['clauses']]
  ```

#### Day 4-5: Clause Classification
- [ ] Define clause taxonomy (10-15 categories)
- [ ] Implement few-shot classification
- [ ] Test classification accuracy
- [ ] Build training dataset (100+ labeled clauses)
  ```python
  CLAUSE_CATEGORIES = [
      "PAYMENT_TERMS",      # APR, monthly payment, down payment
      "PENALTY_LATE",       # Late payment fees
      "PENALTY_EARLY",      # Early termination, prepayment
      "PENALTY_MILEAGE",    # Excess mileage (lease)
      "INSURANCE",          # Insurance requirements
      "MAINTENANCE",        # Maintenance obligations
      "TERMINATION",        # How to end contract
      "WARRANTY",           # Warranty terms
      "DEFAULT",            # What happens if you default
      "ARBITRATION",        # Dispute resolution
      "MISCELLANEOUS"       # Other
  ]
  
  async def classify_clause(clause_text: str) -> str:
      # Use Claude with few-shot examples
      prompt = f"""
      Classify this contract clause into ONE category:
      {', '.join(CLAUSE_CATEGORIES)}
      
      Examples:
      - "Monthly payment is $425" → PAYMENT_TERMS
      - "Late fee is $50" → PENALTY_LATE
      - "$0.25 per mile over 12,000" → PENALTY_MILEAGE
      
      Clause: {clause_text}
      
      Category:
      """
      
      response = await call_claude(prompt, max_tokens=50)
      category = response.strip()
      
      return category if category in CLAUSE_CATEGORIES else "MISCELLANEOUS"
  ```

#### Day 6-7: Entity Extraction
- [ ] Use spaCy for NER (MONEY, PERCENT, DATE)
- [ ] Custom patterns for contract-specific entities
- [ ] Link entities to clauses
  ```python
  import spacy
  from spacy.matcher import Matcher
  
  nlp = spacy.load("en_core_web_lg")
  
  def extract_entities(clause_text: str) -> Dict:
      doc = nlp(clause_text)
      entities = {
          'amounts': [],
          'percentages': [],
          'dates': [],
          'durations': []
      }
      
      # Extract using spaCy NER
      for ent in doc.ents:
          if ent.label_ == "MONEY":
              entities['amounts'].append(ent.text)
          elif ent.label_ == "PERCENT":
              entities['percentages'].append(ent.text)
          elif ent.label_ == "DATE":
              entities['dates'].append(ent.text)
      
      # Custom pattern for APR
      matcher = Matcher(nlp.vocab)
      pattern = [
          {"LIKE_NUM": True},
          {"ORTH": "%"},
          {"LOWER": {"IN": ["apr", "interest", "rate"]}}
      ]
      matcher.add("APR", [pattern])
      matches = matcher(doc)
      
      return entities
  ```

### Week 4 Tasks

#### Day 1-3: Risk Scoring System
- [ ] Define risk factors for each clause type
- [ ] Implement rule-based scoring
- [ ] Add LLM-based risk assessment
- [ ] Combine both approaches
  ```python
  class RiskScorer:
      def __init__(self):
          self.rules = {
              'PENALTY_EARLY': {
                  'high_risk': lambda x: 'prepayment penalty' in x.lower(),
                  'score': 8
              },
              'PAYMENT_TERMS': {
                  'high_risk': lambda x: 'variable rate' in x.lower(),
                  'score': 7
              }
          }
      
      async def calculate_risk(self, clause: Clause) -> int:
          # Rule-based score
          rule_score = self._apply_rules(clause)
          
          # LLM-based assessment
          llm_score = await self._llm_risk_assessment(clause)
          
          # Weighted average
          final_score = int(0.6 * rule_score + 0.4 * llm_score)
          
          return min(10, max(1, final_score))
      
      async def _llm_risk_assessment(self, clause: Clause) -> int:
          prompt = f"""
          Rate the consumer risk of this clause (1-10):
          
          Category: {clause.category}
          Text: {clause.text}
          
          Consider:
          - Is it above market rates?
          - Does it limit consumer rights?
          - Are there hidden costs?
          
          Return ONLY a number 1-10:
          """
          
          response = await call_claude(prompt, max_tokens=10)
          return int(response.strip())
  ```

#### Day 4-5: Integration & Testing
- [ ] Connect all components (segment → classify → extract → score)
- [ ] Build end-to-end pipeline
- [ ] Test with 20+ real contracts
- [ ] Measure accuracy at each step

#### Day 6-7: Optimization
- [ ] Cache results to reduce API calls
- [ ] Parallelize clause processing
- [ ] Add progress tracking
- [ ] Improve error handling

### Deliverables
- ✅ Clause segmentation working
- ✅ Classification >85% accurate
- ✅ Entity extraction functional
- ✅ Risk scoring implemented

---

## 📅 WEEK 5-6: Financial Calculator, Fairness Score & Summary Generator

### Week 5: Financial Calculator & Fairness Score

#### Day 1-2: Core Calculations
- [ ] Implement EMI calculator
- [ ] Build amortization schedule generator
- [ ] Add early payoff calculator
- [ ] Validate against Excel formulas
  ```python
  # app/services/financial_calculator.py
  import math
  from typing import List, Dict
  
  class FinancialCalculator:
      @staticmethod
      def calculate_emi(
          principal: float,
          annual_rate: float,
          tenure_months: int
      ) -> float:
          """
          EMI = [P x R x (1+R)^N] / [(1+R)^N-1]
          where:
          P = Principal
          R = Monthly interest rate (annual_rate/12/100)
          N = Tenure in months
          """
          if annual_rate == 0:
              return principal / tenure_months
          
          monthly_rate = annual_rate / 12 / 100
          emi = (principal * monthly_rate * 
                 math.pow(1 + monthly_rate, tenure_months)) / \
                (math.pow(1 + monthly_rate, tenure_months) - 1)
          
          return round(emi, 2)
      
      @staticmethod
      def generate_amortization_schedule(
          principal: float,
          annual_rate: float,
          tenure_months: int
      ) -> List[Dict]:
          emi = FinancialCalculator.calculate_emi(principal, annual_rate, tenure_months)
          monthly_rate = annual_rate / 12 / 100
          
          schedule = []
          balance = principal
          
          for month in range(1, tenure_months + 1):
              interest = balance * monthly_rate
              principal_paid = emi - interest
              balance -= principal_paid
              
              schedule.append({
                  'month': month,
                  'emi': round(emi, 2),
                  'principal': round(principal_paid, 2),
                  'interest': round(interest, 2),
                  'balance': round(max(0, balance), 2)
              })
          
          return schedule
      
      @staticmethod
      def calculate_savings_early_payoff(
          current_month: int,
          remaining_balance: float,
          monthly_rate: float,
          remaining_emi: int,
          prepayment_penalty: float = 0
      ) -> Dict:
          # Total if you continue
          total_if_continue = remaining_emi * FinancialCalculator.calculate_emi(...)
          
          # Total if you pay off now
          total_if_payoff = remaining_balance + prepayment_penalty
          
          savings = total_if_continue - total_if_payoff
          
          return {
              'savings': round(savings, 2),
              'payoff_amount': round(total_if_payoff, 2),
              'interest_saved': round(total_if_continue - remaining_balance, 2)
          }
  ```

#### Day 3-4: Financial Term Extraction
- [ ] Extract APR from contract
- [ ] Extract principal, tenure, down payment
- [ ] Extract all fees
- [ ] Build structured financial summary
  ```python
  async def extract_financial_terms(contract_text: str) -> FinancialTerms:
      prompt = f"""
      Extract financial terms from this contract.
      Return ONLY valid JSON, no other text.
      
      Contract:
      {contract_text[:3000]}  # First 3000 chars
      
      Return format:
      {{
        "principal": 25000.00,
        "annual_interest_rate": 7.5,
        "tenure_months": 60,
        "down_payment": 2000.00,
        "monthly_payment": 500.00,
        "fees": {{
          "origination_fee": 500,
          "documentation_fee": 200
        }}
      }}
      """
      
      response = await call_claude(prompt, max_tokens=500)
      
      # Parse JSON (handle potential issues)
      try:
          terms = json.loads(response)
          return FinancialTerms(**terms)
      except json.JSONDecodeError:
          # Retry or use regex fallback
          logger.warning("Failed to parse financial terms JSON")
          return extract_with_regex(contract_text)
  ```

#### Day 5-6: Fairness Score Implementation ⭐ NEW FEATURE
- [ ] Design fairness scoring algorithm
- [ ] Implement multi-factor scoring
- [ ] Create score calculation service
- [ ] Validate against real contracts
  ```python
  # app/services/fairness_scorer.py
  from typing import Dict, List
  from models import AnalysisResult, Clause, MarketBenchmark
  from enum import Enum
  
  class FairnessRating(str, Enum):
      EXCELLENT = "excellent"  # 80-100
      GOOD = "good"            # 60-79
      FAIR = "fair"            # 40-59
      POOR = "poor"            # 0-39
  
  class FairnessScorer:
      """
      Calculate contract fairness score (0-100) based on multiple factors.
      """
      
      WEIGHTS = {
          'apr_score': 0.40,      # 40% - Most important
          'fee_score': 0.25,      # 25% - Significant impact
          'penalty_score': 0.20,  # 20% - Can be costly
          'clause_score': 0.15    # 15% - Hidden issues
      }
      
      def __init__(self, market_data: MarketBenchmark):
          self.market_data = market_data
      
      def calculate_fairness_score(
          self,
          analysis: AnalysisResult,
          clauses: List[Clause],
          user_credit_score: int = 700
      ) -> Dict:
          """
          Calculate overall fairness score and breakdown.
          
          Returns:
              {
                  'overall_score': 75,
                  'rating': 'GOOD',
                  'factors': {
                      'apr_score': 85,
                      'fee_score': 70,
                      'penalty_score': 65,
                      'clause_score': 80
                  },
                  'explanation': 'Your contract is GOOD overall...',
                  'improvements': ['Lower APR would increase score by 10 points']
              }
          """
          # Calculate individual factor scores
          apr_score = self._score_apr(analysis.interest_rate, user_credit_score)
          fee_score = self._score_fees(analysis.fees)
          penalty_score = self._score_penalties(clauses)
          clause_score = self._score_clauses(clauses)
          
          # Weighted average
          overall = (
              apr_score * self.WEIGHTS['apr_score'] +
              fee_score * self.WEIGHTS['fee_score'] +
              penalty_score * self.WEIGHTS['penalty_score'] +
              clause_score * self.WEIGHTS['clause_score']
          )
          
          return {
              'overall_score': round(overall, 1),
              'rating': self._get_rating(overall),
              'factors': {
                  'apr_score': apr_score,
                  'fee_score': fee_score,
                  'penalty_score': penalty_score,
                  'clause_score': clause_score
              },
              'explanation': self._generate_explanation(overall, apr_score, fee_score, penalty_score, clause_score),
              'improvements': self._suggest_improvements(apr_score, fee_score, penalty_score, clause_score)
          }
      
      def _score_apr(self, user_apr: float, credit_score: int) -> float:
          """
          Score APR against market benchmarks (0-100).
          Higher score = better (lower) APR.
          """
          # Get market benchmark for user's credit score
          benchmark = self._get_apr_benchmark(credit_score)
          
          if user_apr <= benchmark['excellent']:
              return 100  # Excellent rate
          elif user_apr <= benchmark['good']:
              return 90   # Good rate
          elif user_apr <= benchmark['average']:
              return 70   # Average rate
          elif user_apr <= benchmark['average'] * 1.2:
              return 50   # Slightly above average
          elif user_apr <= benchmark['average'] * 1.5:
              return 30   # High
          else:
              return 10   # Very high
      
      def _score_fees(self, fees: Dict[str, float]) -> float:
          """
          Score total fees against typical market fees.
          """
          total_fees = sum(fees.values())
          
          # Typical fee ranges by contract type
          typical_range = {
              'low': 500,
              'average': 1000,
              'high': 2000
          }
          
          if total_fees <= typical_range['low']:
              return 100
          elif total_fees <= typical_range['average']:
              return 80
          elif total_fees <= typical_range['high']:
              return 50
          else:
              # Penalties for excessive fees
              excess = total_fees - typical_range['high']
              penalty = min(40, (excess / 100) * 5)  # -5 points per $100 over
              return max(10, 50 - penalty)
      
      def _score_penalties(self, clauses: List[Clause]) -> float:
          """
          Score penalty clauses severity.
          Lower penalties = higher score.
          """
          penalty_clauses = [c for c in clauses if 'PENALTY' in c.category]
          
          if not penalty_clauses:
              return 100  # No penalties = excellent
          
          # Check for specific harsh penalties
          has_prepayment_penalty = any('prepayment' in c.text.lower() for c in penalty_clauses)
          has_high_late_fees = any('late' in c.text.lower() and c.risk_score >= 7 for c in penalty_clauses)
          has_repo_charges = any('repossess' in c.text.lower() for c in penalty_clauses)
          
          score = 100
          
          if has_prepayment_penalty:
              score -= 30  # Major negative
          if has_high_late_fees:
              score -= 20
          if has_repo_charges:
              score -= 15
          
          # Additional penalty for number of penalty clauses
          if len(penalty_clauses) > 5:
              score -= 10
          
          return max(0, score)
      
      def _score_clauses(self, clauses: List[Clause]) -> float:
          """
          Score based on overall clause risk.
          Detect hidden or unusual clauses.
          """
          # Average risk score across all clauses
          avg_risk = sum(c.risk_score for c in clauses) / len(clauses)
          
          # Convert risk (1-10) to fairness score (100-0)
          # Risk 1 = Score 100
          # Risk 10 = Score 0
          base_score = 100 - ((avg_risk - 1) * 11.1)
          
          # Penalty for high-risk clauses
          high_risk_count = sum(1 for c in clauses if c.risk_score >= 8)
          if high_risk_count > 0:
              base_score -= (high_risk_count * 5)
          
          return max(0, min(100, base_score))
      
      def _get_rating(self, score: float) -> FairnessRating:
          """Convert numeric score to rating category."""
          if score >= 80:
              return FairnessRating.EXCELLENT
          elif score >= 60:
              return FairnessRating.GOOD
          elif score >= 40:
              return FairnessRating.FAIR
          else:
              return FairnessRating.POOR
      
      def _generate_explanation(self, overall: float, apr: float, fees: float, penalties: float, clauses: float) -> str:
          """Generate human-readable explanation of score."""
          rating = self._get_rating(overall)
          
          if rating == FairnessRating.EXCELLENT:
              base = f"Your contract scored {overall}/100 - Excellent! This is a very fair contract."
          elif rating == FairnessRating.GOOD:
              base = f"Your contract scored {overall}/100 - Good. This contract is generally fair with room for minor improvements."
          elif rating == FairnessRating.FAIR:
              base = f"Your contract scored {overall}/100 - Fair. This contract has some concerning terms that should be negotiated."
          else:
              base = f"Your contract scored {overall}/100 - Poor. This contract has several unfavorable terms. Consider renegotiating or looking elsewhere."
          
          # Add factor details
          weakest = min([
              ('APR', apr),
              ('fees', fees),
              ('penalties', penalties),
              ('clauses', clauses)
          ], key=lambda x: x[1])
          
          detail = f" The weakest area is {weakest[0]} (score: {weakest[1]}/100)."
          
          return base + detail
      
      def _suggest_improvements(self, apr: float, fees: float, penalties: float, clauses: float) -> List[str]:
          """Suggest what would improve the score."""
          improvements = []
          
          if apr < 80:
              potential_gain = 80 - apr
              improvements.append(f"Negotiating a lower APR could increase your score by up to {round(potential_gain * self.WEIGHTS['apr_score'])} points")
          
          if fees < 70:
              improvements.append("Removing or reducing fees could add 5-10 points to your score")
          
          if penalties < 70:
              improvements.append("Waiving prepayment penalties could increase your score by 5-15 points")
          
          return improvements
      
      def _get_apr_benchmark(self, credit_score: int) -> Dict[str, float]:
          """Get APR benchmarks based on credit score."""
          # This should come from database/market data
          # For now, using typical ranges
          if credit_score >= 800:
              return {'excellent': 3.5, 'good': 4.5, 'average': 5.5}
          elif credit_score >= 740:
              return {'excellent': 4.5, 'good': 5.5, 'average': 6.5}
          elif credit_score >= 670:
              return {'excellent': 6.0, 'good': 7.5, 'average': 9.0}
          elif credit_score >= 580:
              return {'excellent': 8.0, 'good': 10.0, 'average': 12.0}
          else:
              return {'excellent': 10.0, 'good': 13.0, 'average': 16.0}
  ```

#### Day 7: Testing & Validation
- [ ] Test calculations against known examples
- [ ] Validate Fairness Score with 10+ real contracts
- [ ] Compare scores to expert legal assessment
- [ ] Build test suite (100+ scenarios)
- [ ] Handle edge cases (0% APR, balloon payments)
- [ ] Document score calculation methodology

### Week 6: Summary Generator

#### Day 1-3: Contract Summarization
- [ ] Design summary template
- [ ] Implement Claude-based summarization
- [ ] Ensure plain language (8th grade reading level)
- [ ] Include key obligations and risks
  ```python
  SUMMARY_PROMPT = """
  Create a plain-language summary of this car lease/loan contract.
  
  Guidelines:
  - Use simple language (8th grade level)
  - 2 pages maximum
  - Include:
    * What you're financing (car make/model)
    * Payment amount and schedule
    * Total cost over contract lifetime
    * Key obligations (what you must do)
    * Key rights (what you can do)
    * Major risks or unfavorable terms
    * How to end the contract
  
  Contract text:
  {contract_text}
  
  Clauses and analysis:
  {clauses_summary}
  
  Financial summary:
  {financial_summary}
  
  Plain-language summary:
  """
  
  async def generate_summary(
      contract_text: str,
      clauses: List[Clause],
      financial: FinancialTerms
  ) -> str:
      # Prepare context
      clauses_summary = "\n".join([
          f"- [{c.category}] {c.text[:100]}... (Risk: {c.risk_score}/10)"
          for c in clauses
      ])
      
      financial_summary = f"""
      - Principal: ${financial.principal:,.2f}
      - APR: {financial.annual_interest_rate}%
      - Monthly Payment: ${financial.monthly_payment:,.2f}
      - Total Repayment: ${financial.monthly_payment * financial.tenure_months:,.2f}
      """
      
      # Call Claude
      response = await call_claude(
          SUMMARY_PROMPT.format(
              contract_text=contract_text[:5000],
              clauses_summary=clauses_summary,
              financial_summary=financial_summary
          ),
          max_tokens=2000
      )
      
      return response
  ```

#### Day 4-5: Overall Risk Assessment
- [ ] Calculate overall contract risk (LOW/MEDIUM/HIGH)
- [ ] Consider: APR vs market, penalties, hidden fees
- [ ] Generate risk explanation
  ```python
  def calculate_overall_risk(
      clauses: List[Clause],
      financial: FinancialTerms,
      market_benchmark: MarketData
  ) -> str:
      # Average clause risk
      avg_clause_risk = sum(c.risk_score for c in clauses) / len(clauses)
      
      # APR risk (compare to market)
      apr_risk = 0
      if financial.annual_interest_rate > market_benchmark.avg_apr + 2:
          apr_risk = 3  # High
      elif financial.annual_interest_rate > market_benchmark.avg_apr + 1:
          apr_risk = 2  # Medium
      else:
          apr_risk = 1  # Low
      
      # Penalty risk (any prepayment penalties?)
      penalty_clauses = [c for c in clauses if 'PENALTY' in c.category]
      penalty_risk = 3 if len(penalty_clauses) > 3 else 1
      
      # Weighted score
      total_score = (
          0.4 * avg_clause_risk +
          0.4 * apr_risk * 2 +  # Scale to 10
          0.2 * penalty_risk * 2
      )
      
      if total_score < 4:
          return "LOW"
      elif total_score < 7:
          return "MEDIUM"
      else:
          return "HIGH"
  ```

#### Day 6-7: Report Generation
- [ ] Create PDF report template
- [ ] Include all sections (summary, clauses, financials)
- [ ] Add charts (amortization, cost breakdown)
- [ ] Enable export/download

### Deliverables
- ✅ Financial calculator working
- ✅ Plain-language summary generator
- ✅ Overall risk assessment
- ✅ Exportable PDF reports

---

## 📅 WEEK 7-8: Frontend Development

### Week 7: Core UI Components

#### Day 1-2: Setup & Layout
- [ ] Initialize Next.js project
- [ ] Set up Tailwind CSS
- [ ] Create layout components (Header, Footer, Sidebar)
- [ ] Implement routing
- [ ] **Design Fairness Score gauge component**
  ```typescript
  // app/layout.tsx
  export default function RootLayout({
    children,
  }: {
    children: React.ReactNode
  }) {
    return (
      <html lang="en">
        <body className="bg-gray-50">
          <Header />
          <main className="container mx-auto px-4 py-8">
            {children}
          </main>
          <Footer />
        </body>
      </html>
    )
  }
  
  // components/FairnessScoreGauge.tsx
  import { useMemo } from 'react'
  
  interface FairnessScoreProps {
    score: number  // 0-100
    rating: 'excellent' | 'good' | 'fair' | 'poor'
    size?: 'sm' | 'md' | 'lg'
  }
  
  export function FairnessScoreGauge({ score, rating, size = 'lg' }: FairnessScoreProps) {
    const color = useMemo(() => {
      if (score >= 80) return 'text-green-600'
      if (score >= 60) return 'text-lime-600'
      if (score >= 40) return 'text-yellow-600'
      return 'text-red-600'
    }, [score])
    
    const bgColor = useMemo(() => {
      if (score >= 80) return 'bg-green-100'
      if (score >= 60) return 'bg-lime-100'
      if (score >= 40) return 'bg-yellow-100'
      return 'bg-red-100'
    }, [score])
    
    const sizeClasses = {
      sm: 'w-24 h-24 text-2xl',
      md: 'w-32 h-32 text-3xl',
      lg: 'w-48 h-48 text-5xl'
    }
    
    return (
      <div className="flex flex-col items-center">
        <div className={`relative ${sizeClasses[size]} rounded-full ${bgColor} flex items-center justify-center border-4 ${color}`}>
          <div className="text-center">
            <div className={`font-bold ${color}`}>{score}</div>
            <div className="text-xs text-gray-600">/ 100</div>
          </div>
        </div>
        <div className={`mt-4 text-xl font-semibold ${color} uppercase`}>
          {rating}
        </div>
      </div>
    )
  }
  ```

#### Day 3-4: Document Upload Interface
- [ ] Build drag-and-drop upload component
- [ ] Add progress indicator
- [ ] Show upload status
- [ ] Handle errors gracefully
  ```typescript
  // components/FileUpload.tsx
  import { useDropzone } from 'react-dropzone'
  import { useState } from 'react'
  
  export function FileUpload() {
    const [uploading, setUploading] = useState(false)
    const [progress, setProgress] = useState(0)
    
    const { getRootProps, getInputProps } = useDropzone({
      accept: { 'application/pdf': ['.pdf'] },
      maxSize: 50 * 1024 * 1024, // 50MB
      onDrop: async (files) => {
        const file = files[0]
        setUploading(true)
        
        const formData = new FormData()
        formData.append('file', file)
        
        try {
          const response = await fetch('/api/documents/upload', {
            method: 'POST',
            body: formData,
            onUploadProgress: (e) => {
              setProgress(Math.round((e.loaded * 100) / e.total))
            }
          })
          
          const data = await response.json()
          router.push(`/analysis/${data.document_id}`)
        } catch (error) {
          console.error('Upload failed:', error)
        } finally {
          setUploading(false)
        }
      }
    })
    
    return (
      <div
        {...getRootProps()}
        className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center cursor-pointer hover:border-blue-500"
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div>
            <div className="text-lg">Uploading... {progress}%</div>
            <div className="w-64 mx-auto mt-4 bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        ) : (
          <div>
            <div className="text-xl font-semibold mb-2">
              Drop your contract PDF here
            </div>
            <div className="text-gray-600">
              or click to select file (max 50MB)
            </div>
          </div>
        )}
      </div>
    )
  }
  ```

#### Day 5-7: Analysis Dashboard
- [ ] Create dashboard layout with **Fairness Score as hero element**
- [ ] Show Fairness Score breakdown by factors
- [ ] Display financial summary
- [ ] Add clause list with filtering
- [ ] Implement score improvement simulator
  ```typescript
  // components/AnalysisDashboard.tsx
  export function AnalysisDashboard({ analysis }: { analysis: Analysis }) {
    return (
      <div className="space-y-8">
        {/* HERO: Fairness Score */}
        <section className="bg-white rounded-lg shadow-lg p-8 text-center">
          <h2 className="text-2xl font-bold mb-6">Contract Fairness Score</h2>
          <FairnessScoreGauge 
            score={analysis.fairness_score.overall_score}
            rating={analysis.fairness_score.rating}
            size="lg"
          />
          <p className="mt-4 text-gray-700 max-w-2xl mx-auto">
            {analysis.fairness_score.explanation}
          </p>
        </section>
        
        {/* Score Breakdown */}
        <section className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold mb-4">Score Breakdown</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <ScoreFactor 
              name="APR"
              score={analysis.fairness_score.factors.apr_score}
              weight={40}
            />
            <ScoreFactor 
              name="Fees"
              score={analysis.fairness_score.factors.fee_score}
              weight={25}
            />
            <ScoreFactor 
              name="Penalties"
              score={analysis.fairness_score.factors.penalty_score}
              weight={20}
            />
            <ScoreFactor 
              name="Clauses"
              score={analysis.fairness_score.factors.clause_score}
              weight={15}
            />
          </div>
        </section>
        
        {/* Financial Summary */}
        <section className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold mb-4">Financial Summary</h3>
          <FinancialSummaryGrid financial={analysis.financial_summary} />
        </section>
        
        {/* Top Recommendations */}
        <section className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold mb-4">
            Top Recommendations 
            <span className="text-sm text-gray-600 ml-2">
              (Could improve score by {analysis.potential_score_gain} points)
            </span>
          </h3>
          <RecommendationList recommendations={analysis.recommendations} />
        </section>
      </div>
    )
  }
  
  function ScoreFactor({ name, score, weight }: { name: string, score: number, weight: number }) {
    const color = score >= 70 ? 'text-green-600' : score >= 50 ? 'text-yellow-600' : 'text-red-600'
    
    return (
      <div className="text-center p-4 border rounded">
        <div className="text-sm text-gray-600 mb-1">{name}</div>
        <div className={`text-3xl font-bold ${color}`}>{score}</div>
        <div className="text-xs text-gray-500">{weight}% weight</div>
        <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
          <div 
            className={`h-2 rounded-full ${score >= 70 ? 'bg-green-600' : score >= 50 ? 'bg-yellow-600' : 'bg-red-600'}`}
            style={{ width: `${score}%` }}
          />
        </div>
      </div>
    )
  }
  ```

### Week 8: Interactive Features

#### Day 1-3: Clause Viewer
- [ ] Build side-by-side view (original + analysis)
- [ ] Add clause highlighting
- [ ] Implement click-to-expand details
- [ ] Color-code by risk level
  ```typescript
  // components/ClauseViewer.tsx
  export function ClauseViewer({ clauses }: { clauses: Clause[] }) {
    const [selectedClause, setSelectedClause] = useState<Clause | null>(null)
    
    const getRiskColor = (score: number) => {
      if (score >= 7) return 'bg-red-100 border-red-500'
      if (score >= 4) return 'bg-yellow-100 border-yellow-500'
      return 'bg-green-100 border-green-500'
    }
    
    return (
      <div className="grid grid-cols-2 gap-4">
        {/* Clause list */}
        <div className="space-y-2">
          {clauses.map((clause) => (
            <div
              key={clause.id}
              className={`p-4 border-l-4 rounded cursor-pointer ${getRiskColor(clause.risk_score)}`}
              onClick={() => setSelectedClause(clause)}
            >
              <div className="font-semibold">{clause.category}</div>
              <div className="text-sm text-gray-700 truncate">
                {clause.text}
              </div>
              <div className="text-xs mt-2">
                Risk: {clause.risk_score}/10
              </div>
            </div>
          ))}
        </div>
        
        {/* Detail panel */}
        {selectedClause && (
          <div className="p-6 bg-white rounded shadow">
            <h3 className="text-lg font-bold mb-4">
              {selectedClause.category}
            </h3>
            <div className="prose prose-sm">
              {selectedClause.text}
            </div>
            <div className="mt-4 p-4 bg-gray-50 rounded">
              <div className="font-semibold">Risk Assessment</div>
              <div>{selectedClause.risk_explanation}</div>
            </div>
          </div>
        )}
      </div>
    )
  }
  ```

#### Day 4-5: Financial Visualizations
- [ ] Build amortization chart (Recharts)
- [ ] Show cost breakdown pie chart
- [ ] Add interactive calculator
  ```typescript
  import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'
  
  export function AmortizationChart({ schedule }: { schedule: AmortizationRow[] }) {
    return (
      <div className="w-full h-96">
        <LineChart width={800} height={400} data={schedule}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" label="Month" />
          <YAxis label="Amount ($)" />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="principal"
            stroke="#3b82f6"
            name="Principal"
          />
          <Line
            type="monotone"
            dataKey="interest"
            stroke="#ef4444"
            name="Interest"
          />
          <Line
            type="monotone"
            dataKey="balance"
            stroke="#10b981"
            name="Remaining Balance"
          />
        </LineChart>
      </div>
    )
  }
  ```

#### Day 6-7: Recommendations Display
- [ ] Show top 5 recommendations
- [ ] Priority sorting
- [ ] Negotiation scripts (expandable)
- [ ] Savings calculator

### Deliverables
- ✅ Responsive web interface
- ✅ Document upload working
- ✅ Interactive dashboard
- ✅ All visualizations functional

---

## 📅 WEEK 9: Renegotiation Engine

### Tasks

#### Day 1-3: Market Benchmarking
- [ ] Build market data module
- [ ] Integrate APR benchmarks by credit score
- [ ] Add typical fee ranges
- [ ] State-specific regulations (if applicable)
  ```python
  # Mock market data (replace with real data later)
  MARKET_BENCHMARKS = {
      'apr_by_credit': {
          (300, 579): {'avg': 14.5, 'good': 12.0},   # Subprime
          (580, 669): {'avg': 10.2, 'good': 8.5},    # Fair
          (670, 739): {'avg': 7.5, 'good': 6.2},     # Good
          (740, 799): {'avg': 5.8, 'good': 4.9},     # Very Good
          (800, 850): {'avg': 4.5, 'good': 3.8},     # Excellent
      },
      'typical_fees': {
          'origination': (0, 500),
          'documentation': (0, 300),
          'dealer_prep': (0, 500),
      }
  }
  
  def get_benchmark_apr(credit_score: int) -> Dict:
      for (min_score, max_score), rates in MARKET_BENCHMARKS['apr_by_credit'].items():
          if min_score <= credit_score <= max_score:
              return rates
      return {'avg': 10.0, 'good': 8.0}  # Default
  ```

#### Day 4-6: Recommendation Generator
- [ ] Identify improvement opportunities
- [ ] Calculate potential savings
- [ ] Generate negotiation scripts
- [ ] Prioritize recommendations
  ```python
  async def generate_recommendations(
      analysis: Analysis,
      user_credit_score: int = 700
  ) -> List[Recommendation]:
      recommendations = []
      
      # 1. APR Reduction
      benchmark = get_benchmark_apr(user_credit_score)
      if analysis.financial.annual_interest_rate > benchmark['good']:
          potential_apr = benchmark['good']
          current_total = analysis.financial.monthly_payment * analysis.financial.tenure_months
          new_emi = FinancialCalculator.calculate_emi(
              analysis.financial.principal,
              potential_apr,
              analysis.financial.tenure_months
          )
          new_total = new_emi * analysis.financial.tenure_months
          savings = current_total - new_total
          
          recommendations.append(Recommendation(
              type="INTEREST_RATE_REDUCTION",
              current_value=f"{analysis.financial.annual_interest_rate}% APR",
              recommended_value=f"{potential_apr}% APR (market rate for credit score {user_credit_score})",
              potential_savings=savings,
              priority=1,
              likelihood="HIGH",
              script=f"Based on my credit score of {user_credit_score}, I qualify for rates around {potential_apr}%. I've seen offers at [competitor] for similar terms. Can we match that rate?"
          ))
      
      # 2. Fee Removal
      for fee_name, fee_amount in analysis.financial.fees.items():
          typical_range = MARKET_BENCHMARKS['typical_fees'].get(fee_name)
          if typical_range and fee_amount > typical_range[1]:
              recommendations.append(Recommendation(
                  type="FEE_REMOVAL",
                  current_value=f"${fee_amount} {fee_name}",
                  recommended_value=f"Negotiate to ${typical_range[1]} or waive entirely",
                  potential_savings=fee_amount - typical_range[1],
                  priority=2,
                  likelihood="MEDIUM",
                  script=f"The ${fee_amount} {fee_name} seems high. Industry standard is around ${typical_range[1]}. Can we reduce this?"
              ))
      
      # 3. Prepayment Penalty Removal
      prepayment_clauses = [c for c in analysis.clauses if 'prepayment' in c.text.lower()]
      if prepayment_clauses:
          recommendations.append(Recommendation(
              type="PREPAYMENT_PENALTY_WAIVER",
              current_value="Prepayment penalty applies",
              recommended_value="Waive prepayment penalty",
              potential_savings=0,  # Calculate based on early payoff scenarios
              priority=3,
              likelihood="MEDIUM",
              script="I value the flexibility to pay off the loan early without penalties. Can we remove the prepayment penalty clause?"
          ))
      
      # Sort by priority and potential savings
      recommendations.sort(key=lambda r: (r.priority, -r.potential_savings))
      
      return recommendations[:10]  # Top 10
  ```

#### Day 7: Testing
- [ ] Test recommendation engine with various contracts
- [ ] Validate savings calculations
- [ ] Refine scripts for clarity

### Deliverables
- ✅ Renegotiation recommendation engine
- ✅ Market benchmarking module
- ✅ Negotiation scripts

---

## 📅 WEEK 10: User Authentication & Polish

### Tasks

#### Day 1-2: Authentication
- [ ] Implement JWT-based auth
- [ ] Add login/signup pages
- [ ] Password reset flow
- [ ] OAuth (Google) integration
  ```python
  # app/auth.py
  from passlib.context import CryptContext
  from jose import jwt
  from datetime import datetime, timedelta
  
  pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
  SECRET_KEY = os.getenv("SECRET_KEY")
  
  def hash_password(password: str) -> str:
      return pwd_context.hash(password)
  
  def verify_password(plain: str, hashed: str) -> bool:
      return pwd_context.verify(plain, hashed)
  
  def create_access_token(user_id: str) -> str:
      payload = {
          "sub": user_id,
          "exp": datetime.utcnow() + timedelta(hours=1)
      }
      return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
  ```

#### Day 3-4: User Dashboard
- [ ] Show user's uploaded documents
- [ ] Display analysis history
- [ ] Usage statistics
- [ ] Subscription management (if applicable)

#### Day 5-7: UI Polish
- [ ] Add loading states
- [ ] Improve error messages
- [ ] Mobile responsiveness
- [ ] Accessibility (WCAG AA)
- [ ] Add tooltips and help text
- [ ] Implement keyboard shortcuts

### Deliverables
- ✅ Working authentication
- ✅ User dashboard
- ✅ Polished UI

---

## 📅 WEEK 11: Testing & Bug Fixes

### Tasks

#### Day 1-3: Integration Testing
- [ ] End-to-end tests (Playwright)
- [ ] Test all user flows
- [ ] Cross-browser testing
- [ ] Performance testing
  ```typescript
  // e2e/contract-analysis.spec.ts
  import { test, expect } from '@playwright/test'
  
  test('user can analyze a contract', async ({ page }) => {
    // Login
    await page.goto('http://localhost:3000/login')
    await page.fill('#email', 'test@example.com')
    await page.fill('#password', 'test123')
    await page.click('button[type=submit]')
    
    // Upload contract
    await page.goto('http://localhost:3000/upload')
    await page.setInputFiles('#file-upload', 'tests/fixtures/sample_lease.pdf')
    
    // Wait for processing
    await page.waitForSelector('text=Analysis Complete', { timeout: 60000 })
    
    // Verify dashboard
    await expect(page.locator('text=Risk Score')).toBeVisible()
    await expect(page.locator('text=Financial Summary')).toBeVisible()
    
    // Check recommendations
    await page.click('text=View Recommendations')
    await expect(page.locator('.recommendation-card').first()).toBeVisible()
  })
  ```

#### Day 4-5: Security Audit
- [ ] SQL injection tests
- [ ] XSS vulnerability checks
- [ ] CSRF protection
- [ ] File upload security (virus scanning)
- [ ] Rate limiting tests

#### Day 6-7: Bug Fixes & Optimization
- [ ] Fix identified bugs
- [ ] Optimize slow queries
- [ ] Reduce bundle size
- [ ] Improve caching

### Deliverables
- ✅ Test coverage >80%
- ✅ All critical bugs fixed
- ✅ Security hardened

---

## 📅 WEEK 12: Launch Preparation

### Tasks

#### Day 1-2: Documentation
- [ ] Write user guide
- [ ] Create FAQ
- [ ] API documentation (if applicable)
- [ ] Internal runbooks

#### Day 3-4: Deployment
- [ ] Set up production environment (AWS)
- [ ] Configure CI/CD for production
- [ ] Set up monitoring (Sentry, Datadog)
- [ ] Configure backups
- [ ] SSL certificates

#### Day 5: Beta Testing
- [ ] Invite 10-20 beta users
- [ ] Collect feedback
- [ ] Make final adjustments

#### Day 6-7: Marketing & Launch
- [ ] Create landing page
- [ ] Write launch blog post
- [ ] Social media posts
- [ ] Product Hunt submission
- [ ] Email announcement

### Deliverables
- ✅ Production deployment
- ✅ Monitoring in place
- ✅ Public launch

---

## 🎉 Post-Launch (Week 13+)

### Ongoing Tasks
- Monitor user feedback
- Track key metrics (conversions, errors)
- Iterate on features
- Fix bugs
- Collect user negotiation stories for training data

---

## 🚀 PHASE 2: Interactive Negotiation Bot (Weeks 13-16)

### Overview
Build conversational AI assistant to help users negotiate in real-time. This transforms CARLO from analysis tool to active negotiation partner.

---

### Week 13: Negotiation Bot Foundation

#### Goals
- Set up conversation management infrastructure
- Build basic chat interface
- Implement context-aware responses

#### Tasks

**Day 1-2: Chat Infrastructure**
- [ ] Set up WebSocket server for real-time chat
- [ ] Create conversation state management (Redis)
- [ ] Build chat API endpoints
  ```python
  POST /api/v1/chat/start          # Start new chat session
  POST /api/v1/chat/message        # Send message
  GET  /api/v1/chat/history        # Get conversation history
  DELETE /api/v1/chat/end          # End session
  ```

**Day 3-4: Context Builder**
- [ ] Build context extraction from contract analysis
- [ ] Create user profile integration
- [ ] Implement market data retrieval for real-time comparisons
  ```python
  class NegotiationContext:
      def __init__(self, analysis: Analysis, user: User):
          self.contract_fairness_score = analysis.fairness_score
          self.weak_points = self._identify_weak_points(analysis)
          self.user_leverage = self._calculate_leverage(analysis, user)
          self.market_data = self._get_current_market_data(user.credit_score)
  ```

**Day 5-7: Basic Conversational AI**
- [ ] Implement Claude-based chat responses
- [ ] Create prompt templates for common scenarios
- [ ] Add conversation memory (track last 10-15 exchanges)
- [ ] Test with 20+ example conversations

**Deliverables:**
- ✅ Working chat backend
- ✅ Context-aware responses
- ✅ Conversation memory

---

### Week 14: Advanced Conversation Features

#### Goals
- Handle complex negotiation scenarios
- Implement role-play mode
- Add multi-turn dialogue support

#### Tasks

**Day 1-3: Scenario Handling**
- [ ] Build 25+ negotiation scenario templates:
  - Dealer won't budge on APR
  - Offering to remove some fees
  - Pushing add-ons/insurance
  - Time pressure tactics
  - "Best I can do" situations
- [ ] Implement scenario detection
- [ ] Create specific response strategies per scenario

**Day 4-5: Role-Play Mode**
- [ ] Build AI dealer simulator
- [ ] Create realistic dealer objections
- [ ] Provide real-time coaching feedback
  ```python
  @app.post("/chat/roleplay")
  async def roleplay(
      user_statement: str,
      session_id: str
  ):
      # AI plays dealer
      dealer_response = generate_dealer_response(user_statement)
      
      # AI coaches user
      feedback = generate_coaching_feedback(user_statement)
      
      return {
          "dealer_says": dealer_response,
          "coach_tip": feedback,
          "suggested_response": "Try this..."
      }
  ```

**Day 6-7: Dialogue Refinement**
- [ ] Implement context tracking across turns
- [ ] Handle topic switches
- [ ] Add clarifying questions when user is vague
- [ ] Test with user role-playing sessions

**Deliverables:**
- ✅ 25+ scenarios handled
- ✅ Role-play mode working
- ✅ Multi-turn conversations

---

### Week 15: Multi-Channel Integration

#### Goals
- Deploy bot to multiple channels
- Optimize for mobile/on-the-go use
- Add notification system

#### Tasks

**Day 1-3: WhatsApp Integration**
- [ ] Set up Twilio Business API
- [ ] Create WhatsApp webhook handler
- [ ] Adapt responses for SMS character limits
- [ ] Test message delivery and responses
  ```python
  from twilio.rest import Client
  
  @app.post("/webhook/whatsapp")
  async def whatsapp_webhook(message: TwilioMessage):
      # Extract user message
      user_msg = message.Body
      user_id = get_or_create_user(message.From)
      
      # Get bot response
      response = await chat_service.respond(user_id, user_msg)
      
      # Send via WhatsApp
      client.messages.create(
          from_='whatsapp:+14155238886',
          body=response,
          to=message.From
      )
  ```

**Day 4-5: SMS Support**
- [ ] Set up Twilio Programmable SMS
- [ ] Create SMS webhook
- [ ] Implement condensed responses for SMS
- [ ] Add SMS opt-in/opt-out

**Day 6-7: Mobile Web Optimization**
- [ ] Build mobile-responsive chat UI
- [ ] Add push notifications for new messages
- [ ] Optimize for low-bandwidth
- [ ] Test on various mobile devices

**Deliverables:**
- ✅ WhatsApp bot live
- ✅ SMS support
- ✅ Mobile-optimized interface

---

### Week 16: Intelligence & Launch

#### Goals
- Train bot on real negotiation outcomes
- Add analytics and feedback loop
- Public beta launch

#### Tasks

**Day 1-2: Outcome Tracking**
- [ ] Add negotiation outcome collection
  ```python
  @app.post("/chat/outcome")
  async def record_outcome(
      session_id: str,
      outcome: NegotiationOutcome
  ):
      # User reports: "I got APR reduced from 8.5% to 7.2%"
      # Track which recommendations worked
      # Feed back into success likelihood model
  ```
- [ ] Build success analytics dashboard
- [ ] Track which scripts/strategies work best

**Day 3-4: Continuous Learning**
- [ ] Implement feedback collection after each negotiation
- [ ] Build recommendation success rate tracking
- [ ] Update market benchmarks based on successful negotiations
- [ ] A/B test different negotiation scripts

**Day 5: Testing & QA**
- [ ] Run 50+ simulated conversations
- [ ] Test edge cases (user confusion, off-topic, abuse)
- [ ] Verify all channels working
- [ ] Load test (100 concurrent users)

**Day 6-7: Beta Launch**
- [ ] Deploy to production
- [ ] Invite 50 beta users from Phase 1
- [ ] Create tutorial videos for negotiation bot
- [ ] Monitor usage and collect feedback
- [ ] Write launch blog post

**Deliverables:**
- ✅ Negotiation Bot v1.0 live
- ✅ 50+ beta users onboarded
- ✅ Analytics tracking outcomes
- ✅ Feedback loop active

---

### Phase 2 Success Metrics

**Engagement:**
- 60%+ of users try negotiation bot
- Average 8+ messages per conversation
- 40%+ return for multiple sessions

**Outcomes:**
- 50%+ report successfully negotiating better terms
- Average savings: $500+ per successful negotiation
- User confidence increase: 70%+ report feeling more confident

**Technical:**
- Response time < 3 seconds
- 99.5% uptime
- Handle 500+ concurrent chat sessions

---

### Phase 2 Optional Enhancements
- Voice integration (phone call support)
- Video role-play with avatars
- Integration with calendar (schedule dealer appointments)
- Community feature (share success stories)
- Dealer-facing tool (help dealers understand fair pricing)

---

## 📊 Success Metrics

### MVP Success Criteria
- [ ] 95%+ document processing accuracy
- [ ] < 30 second average processing time
- [ ] 100% financial calculation accuracy
- [ ] < 5% error rate
- [ ] 10 beta users successfully analyze contracts
- [ ] Average user satisfaction score > 4/5

### Launch Goals (Month 1)
- 100 signups
- 50 contracts analyzed
- 10 paid conversions
- < 1% error rate
- NPS > 30

---

## 🛠️ Daily Standup Template

```markdown
### What I did yesterday:
- [ ] Task 1
- [ ] Task 2

### What I'm doing today:
- [ ] Task 3
- [ ] Task 4

### Blockers:
- None / [describe blocker]

### Risks:
- [Any concerns about timeline, technical approach, etc.]
```

---

## 📝 Notes

- This roadmap assumes 1 full-time developer with AI assistance
- Adjust timeline if working part-time or with a team
- Each task is roughly 1 day of work; some may take longer
- Don't skip testing - it's crucial for a legal/financial product
- Focus on MVP; resist feature creep

---

**Project Start**: February 17, 2026  
**MVP Launch**: May 12, 2026 (12 weeks)  
**Owner**: [Your Name]