
"""
Survey Model - Represents survey metadata
"""
from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class Survey(db.Model):
    __tablename__ = 'surveys'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(50), default='draft')  # draft, processing, completed, error

    # Survey configuration
    metadata = db.Column(JSON, default={})

    # Relationships
    datasets = db.relationship('Dataset', backref='survey', lazy=True, cascade='all, delete-orphan')
    cleaning_configs = db.relationship('CleaningConfig', backref='survey', lazy=True, cascade='all, delete-orphan')
    weight_configs = db.relationship('WeightConfig', backref='survey', lazy=True, cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='survey', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Survey {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'metadata': self.metadata
        }
