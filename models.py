"""
models.py – SQLAlchemy ORM models: articles, claims, users
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    url = Column(String(2048), nullable=True)
    title = Column(String(512), nullable=True)
    content = Column(Text, nullable=True)
    credibility_score = Column(Float, nullable=True)
    verdict = Column(String(64), nullable=True)   # FAKE | UNVERIFIED | CREDIBLE
    analysed_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    claims = relationship("Claim", back_populates="article", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Article id={self.id} verdict={self.verdict}>"


class Claim(Base):
    __tablename__ = "claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False)
    claim_text = Column(Text, nullable=False)
    score = Column(Float, nullable=True)
    explanation = Column(Text, nullable=True)
    sources_checked = Column(JSON, default=list)   # list of source URLs / names

    # Relationship
    article = relationship("Article", back_populates="claims")

    def __repr__(self):
        return f"<Claim id={self.id} score={self.score}>"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(256), unique=True, nullable=False, index=True)
    extension_token = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"
