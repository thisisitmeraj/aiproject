"""
routers/articles.py – CRUD endpoints for articles
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import ArticleCreate, ArticleOut
from backend import models

router = APIRouter()


@router.get("/articles", response_model=List[ArticleOut])
def list_articles(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Return a paginated list of analysed articles."""
    articles = db.query(models.Article).order_by(models.Article.analysed_at.desc()).offset(skip).limit(limit).all()
    return articles


@router.get("/articles/{article_id}", response_model=ArticleOut)
def get_article(article_id: UUID, db: Session = Depends(get_db)):
    """Return a single article by UUID."""
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.delete("/articles/{article_id}")
def delete_article(article_id: UUID, db: Session = Depends(get_db)):
    """Delete an article and its related claims."""
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    db.delete(article)
    db.commit()
    return {"message": "Article deleted successfully"}
