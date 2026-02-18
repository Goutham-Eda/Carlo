# src/backend/models.py
"""
Database models for CARLO application.
SQLAlchemy ORM models for Users, Documents, Clauses, Analyses, and Recommendations.
"""

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Enum, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid
import enum


# Enums for type safety
class DocumentType(str, enum.Enum):
    """Type of contract document"""
    LEASE = "lease"
    LOAN = "loan"
    UNKNOWN = "unknown"


class ProcessingStatus(str, enum.Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskLevel(str, enum.Enum):
    """Overall risk assessment"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SubscriptionTier(str, enum.Enum):
    """User subscription level"""
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"


# Models
class User(Base):
    """User account model"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Subscription
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    credits_remaining = Column(Integer, default=1)  # Free tier gets 1 analysis
    
    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(email={self.email}, tier={self.subscription_tier})>"


class Document(Base):
    """Uploaded contract document"""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # File metadata
    filename = Column(String(255), nullable=False)
    s3_key = Column(String(500), nullable=False)  # S3 or local storage path
    file_size_bytes = Column(Integer)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Document info
    document_type = Column(Enum(DocumentType), default=DocumentType.UNKNOWN)
    processing_status = Column(Enum(ProcessingStatus), default=ProcessingStatus.UPLOADED, index=True)
    error_message = Column(Text)  # If processing failed
    
    # Extracted content
    extracted_text = Column(Text)
    ocr_confidence = Column(Float)  # 0-1 confidence score if OCR was used
    
    # Relationships
    user = relationship("User", back_populates="documents")
    clauses = relationship("Clause", back_populates="document", cascade="all, delete-orphan")
    analysis = relationship("AnalysisResult", back_populates="document", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(filename={self.filename}, status={self.processing_status})>"


class Clause(Base):
    """Individual contract clause"""
    __tablename__ = "clauses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    # Clause content
    clause_number = Column(Integer)  # Order in document
    clause_text = Column(Text, nullable=False)
    clause_title = Column(String(500))  # Optional section title
    
    # Classification
    category = Column(String(50))  # PAYMENT_TERMS, PENALTY_LATE, etc.
    
    # Risk assessment
    risk_score = Column(Integer)  # 1-10
    risk_explanation = Column(Text)
    
    # Metadata
    page_number = Column(Integer)
    extracted_entities = Column(JSON)  # {'amount': 500, 'currency': 'USD', 'date': '2024-01-01'}
    
    # Relationships
    document = relationship("Document", back_populates="clauses")
    
    def __repr__(self):
        return f"<Clause(category={self.category}, risk={self.risk_score})>"


class AnalysisResult(Base):
    """Complete analysis of a contract"""
    __tablename__ = "analysis_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Overall assessment
    overall_risk_score = Column(Enum(RiskLevel))
    contract_summary = Column(Text)  # Plain-language summary
    
    # Fairness Score (NEW)
    fairness_score = Column(Float)  # 0-100
    fairness_rating = Column(String(20))  # EXCELLENT, GOOD, FAIR, POOR
    fairness_factors = Column(JSON)  # {'apr_score': 85, 'fee_score': 70, ...}
    fairness_explanation = Column(Text)
    potential_score_gain = Column(Float)  # How much score could improve with recommendations
    
    # Financial terms (extracted)
    principal_amount = Column(Float)
    interest_rate = Column(Float)  # APR
    tenure_months = Column(Integer)
    monthly_payment = Column(Float)
    down_payment = Column(Float)
    
    # Calculated financial metrics
    total_repayment = Column(Float)
    total_interest = Column(Float)
    
    # Penalty details (critical for fairness score calculation)
    penal_interest = Column(Float)  # Late payment charges
    cheque_dishonour_fee = Column(Float)  # Bounced payment penalty
    prepayment_charges = Column(Float)  # Early repayment penalty
    repossession_charges = Column(Float)  # Vehicle recovery costs
    early_termination_fee = Column(Float)  # Contract exit penalty
    
    # Additional details
    fees = Column(JSON)  # {'origination_fee': 500, 'doc_fee': 200, 'dealer_prep': 300}
    vehicle_info = Column(JSON)  # {'make': 'Honda', 'model': 'Accord', 'year': 2024}
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processing_time_seconds = Column(Float)
    
    # Relationships
    document = relationship("Document", back_populates="analysis")
    recommendations = relationship("Recommendation", back_populates="analysis", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AnalysisResult(fairness={self.fairness_score}, risk={self.overall_risk_score}, monthly=${self.monthly_payment})>"


class Recommendation(Base):
    """Renegotiation recommendation"""
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analysis_results.id", ondelete="CASCADE"), nullable=False)
    
    # Recommendation details
    recommendation_type = Column(String(50))  # INTEREST_RATE_REDUCTION, FEE_REMOVAL, etc.
    current_value = Column(Text)  # "8.5% APR"
    recommended_value = Column(Text)  # "6.9% APR"
    
    # Impact
    potential_savings = Column(Float)  # Dollar amount
    fairness_score_impact = Column(Float)  # How many points this would add to fairness score
    priority = Column(Integer)  # 1 = highest priority
    success_likelihood = Column(String(20))  # HIGH, MEDIUM, LOW
    
    # Guidance
    negotiation_script = Column(Text)
    rationale = Column(Text)  # Why this recommendation makes sense
    
    # User feedback (optional)
    was_attempted = Column(Boolean, default=False)
    was_successful = Column(Boolean)
    user_notes = Column(Text)
    
    # Relationships
    analysis = relationship("AnalysisResult", back_populates="recommendations")
    
    def __repr__(self):
        return f"<Recommendation(type={self.recommendation_type}, savings=${self.potential_savings}, score_gain={self.fairness_score_impact})>"


class AuditLog(Base):
    """Audit log for tracking user actions"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100))  # upload_document, view_analysis, etc.
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45))  # IPv6 compatible
    metadata = Column(JSON)  # Additional context
    
    def __repr__(self):
        return f"<AuditLog(action={self.action}, time={self.timestamp})>"


# Optional: Market benchmark data (for recommendation engine)
class MarketBenchmark(Base):
    """Market data for benchmarking contracts"""
    __tablename__ = "market_benchmarks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Credit score range
    credit_score_min = Column(Integer)
    credit_score_max = Column(Integer)
    
    # APR benchmarks
    avg_apr = Column(Float)
    good_apr = Column(Float)
    
    # Fee benchmarks
    typical_fees = Column(JSON)  # {'origination': [0, 500], 'doc': [0, 300]}
    
    # Metadata
    data_source = Column(String(255))
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<MarketBenchmark(credit={self.credit_score_min}-{self.credit_score_max}, apr={self.avg_apr})>"