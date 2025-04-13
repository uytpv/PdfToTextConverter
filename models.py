from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Keyword(db.Model):
    """Model for keywords to search for in PDFs"""
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # One-to-many relationship with KeywordMatches
    matches = db.relationship('KeywordMatch', backref='keyword', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Keyword {self.keyword}>"


class KeywordMatch(db.Model):
    """Model for storing extracted content related to keywords"""
    id = db.Column(db.Integer, primary_key=True)
    keyword_id = db.Column(db.Integer, db.ForeignKey('keyword.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    page_number = db.Column(db.Integer, nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<KeywordMatch {self.id} - {self.file_name}>"


class ProcessedFile(db.Model):
    """Model for tracking processed PDF files"""
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False, unique=True)
    file_path = db.Column(db.Text, nullable=False)
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False, default='processed')  # processed, failed, etc.
    
    def __repr__(self):
        return f"<ProcessedFile {self.file_name}>"