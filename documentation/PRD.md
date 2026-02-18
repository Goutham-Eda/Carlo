# Product Requirements Document (PRD)
# CARLO - Contract Analysis, Review, and Loan Optimization

**Version**: 1.0  
**Date**: February 14, 2026  
**Status**: Draft  
**Owner**: Product Team

---

## 1. Executive Summary

### 1.1 Product Overview
CARLO is an AI-powered platform that helps consumers understand, evaluate, and negotiate car lease and loan contracts. By automating contract analysis and providing actionable insights, CARLO empowers users to make informed financial decisions and potentially save thousands of dollars.

### 1.2 Business Objectives
- **Primary**: Democratize access to contract analysis expertise
- **Secondary**: Reduce consumer financial risk in auto financing
- **Tertiary**: Create a scalable B2C/B2B2C product with clear ROI

### 1.3 Success Metrics
- **User Acquisition**: 10,000 users in first 6 months
- **Contract Analysis**: 5,000 contracts analyzed
- **User Satisfaction**: NPS > 50
- **Savings Generated**: $5M+ in identified savings for users
- **Conversion Rate**: 15% from free to paid tier

---

## 2. Target Users

### 2.1 Primary Personas

#### Persona 1: First-Time Car Buyer
- **Demographics**: 25-35 years old, limited credit history
- **Pain Points**: 
  - Overwhelmed by contract complexity
  - Worried about hidden fees
  - No negotiation experience
- **Goals**: Understand what they're signing, avoid bad deals
- **Tech Savviness**: Medium to high

#### Persona 2: Family Upgrading Vehicle
- **Demographics**: 35-50 years old, established credit
- **Pain Points**: 
  - Time-constrained, can't read 50-page contracts
  - Want to optimize for lowest total cost
  - Previous bad experience with auto financing
- **Goals**: Quick analysis, clear cost comparison
- **Tech Savviness**: Medium

#### Persona 3: Business Fleet Manager
- **Demographics**: 30-55 years old, manages multiple vehicles
- **Pain Points**: 
  - Reviewing dozens of contracts manually
  - Need standardized comparison
  - Must justify decisions to management
- **Goals**: Bulk analysis, standardized reporting
- **Tech Savviness**: High

### 2.2 Secondary Personas
- Financial advisors recommending the tool
- Dealership finance managers (for transparency/trust)
- Consumer advocacy organizations

---

## 3. Core Features & Requirements

### 3.1 Feature 1: Document Upload & Processing

#### User Story
*"As a car buyer, I want to upload my contract PDF so that I can get it analyzed without manual data entry."*

#### Requirements
- **FR-1.1**: Support PDF, DOC, DOCX upload (max 50MB)
- **FR-1.2**: OCR for scanned documents with 95%+ accuracy
- **FR-1.3**: Process documents in <30 seconds
- **FR-1.4**: Support multi-page contracts (up to 100 pages)
- **FR-1.5**: Detect and handle different contract formats (lease vs loan)

#### Acceptance Criteria
- [ ] User can drag-and-drop PDF file
- [ ] System extracts text with >95% accuracy
- [ ] Processing time < 30 seconds for 95% of documents
- [ ] Error handling for corrupted/unsupported files
- [ ] Progress indicator during upload

---

### 3.2 Feature 2: Clause Identification & Classification

#### User Story
*"As a user, I want to see all important clauses highlighted and categorized so I know what to focus on."*

#### Requirements
- **FR-2.1**: Identify and extract all contractual clauses
- **FR-2.2**: Classify clauses into categories:
  - Payment Terms (APR, monthly payment, down payment)
  - Penalties (early termination, late payment, excess mileage)
  - Insurance Requirements
  - Maintenance Obligations
  - Termination Conditions
  - Warranty & Liability
  - Miscellaneous Terms
- **FR-2.3**: Extract key entities: dates, amounts, percentages, parties
- **FR-2.4**: Link related clauses (e.g., penalty clause to payment clause)

#### Acceptance Criteria
- [ ] >90% clause identification accuracy
- [ ] All clauses assigned to correct category
- [ ] Key financial terms extracted correctly
- [ ] Visual categorization in UI

---

### 3.3 Feature 3: Risk Assessment & Contract Fairness Score

#### User Story
*"As a user, I want to know which parts of my contract are risky or unfavorable so I can focus on those during negotiation."*

#### Requirements
- **FR-3.1**: Assign risk score to each clause (1-10 scale)
- **FR-3.2**: Risk factors include:
  - Prepayment penalties
  - Variable interest rates
  - Balloon payments
  - Aggressive late fees (Penal Interest)
  - Cheque dishonour fees
  - Repossession charges
  - Early termination penalties
  - Mandatory arbitration
  - Unreasonable insurance requirements
  - Hidden fees
- **FR-3.3**: Overall Contract Fairness Score (0-10 scale)
  - Combines: APR competitiveness, fee transparency, penalty severity, consumer rights protection
  - 8-10: Excellent (fair contract, competitive terms)
  - 5-7: Fair (some negotiation opportunities)
  - 0-4: Poor (multiple red flags, negotiate heavily)
- **FR-3.4**: Comparison with market benchmarks
- **FR-3.5**: Explanation for each risk rating
- **FR-3.6**: Fairness score breakdown showing contribution of each factor

#### Acceptance Criteria
- [ ] Every clause has risk score
- [ ] Risk explanations are clear and actionable
- [ ] Fairness Score prominently displayed (larger than risk indicators)
- [ ] Score breakdown shows: APR fairness (40%), Fee fairness (30%), Penalty severity (20%), Terms clarity (10%)
- [ ] Visual fairness indicator (gauge/meter visualization)
- [ ] Color-coded: Green (8-10), Yellow (5-7), Red (0-4)

---

### 3.4 Feature 4: Financial Impact Calculator

#### User Story
*"As a user, I want to see exactly how much this contract will cost me over time, including all fees and penalties."*

#### Requirements
- **FR-4.1**: Calculate and display:
  - Monthly payment (EMI)
  - Total amount payable
  - Total interest paid
  - Principal amount
  - Down payment impact
  - Estimated tax
- **FR-4.2**: Scenario modeling:
  - Early payoff scenarios
  - Late payment impact
  - Excess mileage cost (for leases)
  - Different down payment amounts
- **FR-4.3**: Visual amortization schedule
- **FR-4.4**: Cost breakdown by category
- **FR-4.5**: Comparison with alternative financing options

#### Acceptance Criteria
- [ ] All calculations are accurate to the penny
- [ ] Interactive calculator for "what-if" scenarios
- [ ] Visual charts for cost breakdown
- [ ] Export calculations to PDF

---

### 3.5 Feature 5: AI Contract Summarization

#### User Story
*"As a busy consumer, I want a plain-language summary of my contract so I understand key terms without reading 50 pages."*

#### Requirements
- **FR-5.1**: Generate 2-page summary in plain language
- **FR-5.2**: Summary includes:
  - Key obligations (what you must do)
  - Key rights (what you can do)
  - Payment schedule
  - Termination conditions
  - Major risks
  - Important dates
- **FR-5.3**: Highlight surprising or unusual terms
- **FR-5.4**: Reading level: 8th grade or below
- **FR-5.5**: Available in multiple languages (Phase 2)

#### Acceptance Criteria
- [ ] Summary generated in <10 seconds
- [ ] Covers all critical contract elements
- [ ] No legal jargon
- [ ] User comprehension >85% (user testing)

---

### 3.6 Feature 6: Contract Fairness Score

#### User Story
*"As a user, I want to see at-a-glance how fair my contract is compared to market standards so I can quickly decide if it's worth signing."*

#### Requirements
- **FR-6.1**: Calculate overall fairness score (0-100 scale)
- **FR-6.2**: Score based on multiple factors:
  - APR vs market average for credit score (40% weight)
  - Total fees vs typical market fees (25% weight)
  - Penalty severity (20% weight)
  - Hidden/unusual clauses (15% weight)
- **FR-6.3**: Provide categorical rating:
  - 80-100: EXCELLENT (green)
  - 60-79: GOOD (light green)
  - 40-59: FAIR (yellow)
  - 0-39: POOR (red)
- **FR-6.4**: Show score breakdown by factor
- **FR-6.5**: Explain what's pulling score down
- **FR-6.6**: Compare to average contracts in user's area
- **FR-6.7**: Visual gauge/meter display

#### Acceptance Criteria
- [ ] Score accurately reflects contract quality
- [ ] Score breakdown shows contribution of each factor
- [ ] Visual display is intuitive and eye-catching
- [ ] Score validated against expert legal review (10+ contracts)
- [ ] 90%+ correlation between score and expert assessment

---

### 3.7 Feature 7: Renegotiation Recommendation Engine

#### User Story
*"As a user, I want specific suggestions on what to negotiate so I can get better terms from the dealer."*

#### Requirements
- **FR-7.1**: Generate specific, actionable recommendations:
  - "Request APR reduction from 8.5% to 6.9% (market average for your credit score)"
  - "Negotiate removal of $500 dealer prep fee"
  - "Request waiver of prepayment penalty"
- **FR-7.2**: Prioritize recommendations by:
  - Potential savings
  - Likelihood of success
  - Effort required
- **FR-7.3**: Provide negotiation scripts/talking points
- **FR-7.4**: Show comparable market data
- **FR-7.5**: Estimate total potential savings
- **FR-7.6**: Track which recommendations were successful (user feedback)
- **FR-7.7**: Link recommendations to Fairness Score factors

#### Acceptance Criteria
- [ ] At least 5 actionable recommendations per contract
- [ ] Recommendations are realistic and achievable
- [ ] Clear savings calculation for each recommendation
- [ ] Scripts are professional and effective
- [ ] Each recommendation shows impact on Fairness Score if implemented

---

### 3.8 Feature 8: User Dashboard & Interface

#### User Story
*"As a user, I want an intuitive interface that guides me through understanding my contract step-by-step."*

#### Requirements
- **FR-8.1**: Dashboard showing:
  - **Fairness Score (prominent, large visual gauge)**
  - Contract overview
  - Risk score breakdown
  - Financial summary
  - Top recommendations
- **FR-8.2**: Interactive contract viewer:
  - Side-by-side original and analysis
  - Click clauses to see explanation
  - Highlight risk areas
  - Color-code by fairness impact
- **FR-8.3**: Export options:
  - PDF report (including Fairness Score)
  - Email summary
  - Share with advisor
- **FR-8.4**: Mobile-responsive design
- **FR-8.5**: Guided tutorial for first-time users
- **FR-8.6**: Before/After comparison (current score vs. potential score if recommendations implemented)

#### Acceptance Criteria
- [ ] Dashboard loads in <2 seconds
- [ ] Fairness Score is the first thing users see
- [ ] All critical info visible without scrolling
- [ ] Mobile experience is seamless
- [ ] User can complete analysis in <5 minutes
- [ ] Score breakdown is interactive and explanatory

---

### 3.9 Feature 9: Interactive Negotiation Bot (Phase 2)

#### User Story
*"As a user preparing to negotiate with a dealer, I want real-time AI guidance so I can confidently discuss better terms and respond to dealer objections."*

#### Requirements
- **FR-9.1**: Conversational AI assistant for negotiation preparation and real-time support
- **FR-9.2**: Context-aware responses based on:
  - User's contract analysis and Fairness Score
  - Market benchmarks for user's credit profile
  - Common dealer negotiation tactics
  - Successful negotiation patterns from other users
- **FR-9.3**: Multi-turn dialogue capabilities with natural conversation flow
- **FR-9.4**: Handle common negotiation scenarios:
  - "The dealer says they can't lower the APR. What should I do?"
  - "They're offering to remove the doc fee but not the prep fee. Is that good?"
  - "How do I ask about prepayment penalties without seeming difficult?"
  - "They say this is the best rate for my credit score. Is that true?"
- **FR-9.5**: Provide personalized negotiation scripts adapted to user's situation
- **FR-9.6**: Role-play mode: Practice negotiation with AI playing dealer
- **FR-9.7**: Track negotiation progress and update recommendations based on dealer responses
- **FR-9.8**: Multi-channel availability:
  - Web chat (primary)
  - WhatsApp Business integration
  - SMS support (for on-the-go questions)
- **FR-9.9**: Save conversation history and insights for future reference

#### Acceptance Criteria
- [ ] Bot maintains full context from user's contract analysis
- [ ] Responses are personalized to user's specific contract and credit profile
- [ ] Can handle 25+ common negotiation scenarios and dealer objections
- [ ] Response time < 3 seconds per message
- [ ] Maintains conversation context across 10+ message exchanges
- [ ] Provides specific talking points and data, not generic advice
- [ ] Role-play mode accurately simulates dealer responses
- [ ] User satisfaction rating > 4.2/5
- [ ] 70%+ of users report feeling more confident after using bot

---

## 4. Non-Functional Requirements

### 4.1 Performance
- **NFR-1**: Document processing < 30 seconds (95th percentile)
- **NFR-2**: Page load time < 2 seconds
- **NFR-3**: Support 1,000 concurrent users
- **NFR-4**: 99.9% uptime during business hours

### 4.2 Security
- **NFR-5**: All data encrypted in transit (TLS 1.3)
- **NFR-6**: All data encrypted at rest (AES-256)
- **NFR-7**: GDPR/CCPA compliant data handling
- **NFR-8**: Documents deleted after 30 days (or user request)
- **NFR-9**: No PII sold to third parties
- **NFR-10**: SOC 2 Type II compliance (within 12 months)

### 4.3 Accuracy
- **NFR-11**: Clause extraction accuracy > 95%
- **NFR-12**: Financial calculation accuracy: 100%
- **NFR-13**: Risk assessment validated by legal experts
- **NFR-14**: False positive rate < 5% for risk detection

### 4.4 Usability
- **NFR-15**: Time to first value < 3 minutes
- **NFR-16**: User can complete primary task without help
- **NFR-17**: Accessibility: WCAG 2.1 AA compliant
- **NFR-18**: Support for screen readers

### 4.5 Scalability
- **NFR-19**: Architecture supports 100K+ users
- **NFR-20**: Horizontal scaling for AI processing
- **NFR-21**: CDN for global performance

---

## 5. User Flows

### 5.1 Primary Flow: New User Contract Analysis

```
1. User lands on homepage
2. User clicks "Analyze My Contract" CTA
3. User creates account (email/Google/Apple)
4. User uploads contract PDF
5. System processes document (progress bar)
6. User sees analysis dashboard
   - Risk score (big, visual)
   - Financial summary
   - Key highlights
7. User clicks "See Full Analysis"
8. User reviews clause-by-clause breakdown
9. User clicks "Get Renegotiation Tips"
10. User sees recommendations + savings potential
11. User exports report OR saves to dashboard
12. (Optional) User shares success story
```

### 5.2 Secondary Flow: Contract Comparison

```
1. User has multiple contracts
2. User uploads 2-3 contracts
3. System analyzes all
4. User clicks "Compare Contracts"
5. Side-by-side comparison table:
   - APR, total cost, risk score
6. User sees recommendation: "Contract B is best"
7. User proceeds with recommended contract
```

---

## 6. MVP Scope (Phase 1)

### In Scope
✅ PDF upload and text extraction  
✅ Clause classification (10+ categories including all penalty types)  
✅ Detailed risk scoring (1-10 scale per clause)  
✅ **Contract Fairness Score (0-100 with prominent visual gauge)**  
✅ Financial calculator (EMI, total cost, interest, amortization schedule)  
✅ Extraction of critical parameters:
  - APR, EMI, Loan Tenure, Down Payment
  - Penal Interest (late payment charges)
  - Cheque Dishonour Fee
  - Prepayment Charges
  - Repossession Charges
  - Early Termination Fees
✅ Plain-language summary  
✅ Static renegotiation recommendations (top 5-10 with scripts)  
✅ Fairness Score breakdown showing contribution of each factor  
✅ Simple web interface (desktop)  
✅ Single-contract analysis  
✅ Dashboard with Fairness Score prominently displayed  

### Out of Scope (Future Phases)
❌ **Interactive Negotiation Bot** (Phase 2 - Weeks 13-16)  
❌ Mobile apps (native iOS/Android)  
❌ Contract comparison tool  
❌ Multi-language support  
❌ Dealership integrations  
❌ WhatsApp/SMS integration for Negotiation Bot  
❌ Real-time negotiation role-play  
❌ Bulk analysis for businesses  
❌ API for third parties  
❌ Advanced analytics and reporting

### Out of Scope (Future Phases)
❌ Mobile apps  
❌ Contract comparison  
❌ Real-time negotiation chatbot  
❌ Multi-language support  
❌ Dealership integrations  
❌ Bulk analysis for businesses  
❌ API for third parties  
❌ Historical score tracking over time  

---

## 7. Pricing Strategy (Preliminary)

### Free Tier
- 1 contract analysis per month
- Basic risk score
- Financial calculator
- Summary only

### Pro Tier ($29.99 one-time OR $9.99/month)
- Unlimited contract analyses
- Full renegotiation recommendations
- Export reports
- Priority support
- Contract comparison (up to 3)

### Business Tier ($299/month)
- Everything in Pro
- Bulk upload (up to 50 contracts)
- API access
- Custom branding
- Dedicated account manager

---

## 8. Technical Constraints

1. **Legal Disclaimer**: Must clearly state this is not legal advice
2. **Data Retention**: User contracts stored max 30 days
3. **API Costs**: Need to manage OpenAI/Claude API costs (budget: $0.50/analysis)
4. **Accuracy**: Must validate AI output against legal expertise
5. **Jurisdictions**: Start with US contracts only (state-specific rules later)

---

## 9. Dependencies & Risks

### Dependencies
- OpenAI/Anthropic API availability
- PDF parsing library reliability
- Access to market benchmark data
- Legal expert validation

### Risks
| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| AI hallucination on critical terms | High | Medium | Human review for high-risk clauses |
| Legal liability claims | High | Low | Strong disclaimers, insurance |
| API cost overrun | Medium | Medium | Rate limiting, caching |
| Poor user adoption | High | Medium | Strong marketing, free tier |
| Competitor launch | Medium | High | Fast execution, unique features |

---

## 10. Success Criteria

### Launch Criteria (Go/No-Go)
- [ ] 95%+ clause extraction accuracy (validated on 100 contracts)
- [ ] 100% financial calculation accuracy
- [ ] <5% error rate on risk assessment
- [ ] Legal disclaimer approved by counsel
- [ ] Security audit passed
- [ ] Load testing: 100 concurrent users
- [ ] User testing: 8/10 can complete task unassisted

### Post-Launch Metrics (3 months)
- 5,000+ contracts analyzed
- 15% conversion to paid tier
- <5% churn rate
- NPS > 40
- Average savings identified: $2,000+ per contract

---

## 11. Open Questions

1. Should we support international contracts? (complexity vs market size)
2. What's our liability if user relies on incorrect analysis?
3. How do we verify user success in renegotiation?
4. Should we partner with dealerships or stay consumer-focused?
5. Can we train our own models vs relying on OpenAI/Claude?

---

## 12. Appendix

### A. Sample Contract Types Supported
- Traditional auto loan (bank/credit union)
- Dealer financing (BHPH)
- Closed-end lease
- Open-end lease
- Balloon payment loan

### B. Benchmark Data Sources
- Edmunds average APR by credit score
- Federal Reserve consumer credit data
- Industry lease rate reports
- State-specific dealer fee regulations

---

**Document Owner**: Product Manager  
**Last Review**: February 14, 2026  
**Next Review**: March 1, 2026