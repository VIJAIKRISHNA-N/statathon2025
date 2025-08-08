
"""
Dataset Model - Represents uploaded survey data files
"""
from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class Dataset(db.Model):
    __tablename__ = 'datasets'

    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)

    # File information
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))  # csv, excel

    # Data information
    total_rows = db.Column(db.Integer)
    total_columns = db.Column(db.Integer)
    schema_info = db.Column(JSON, default={})  # Column names, types, etc.

    # Processing status
    status = db.Column(db.String(50), default='uploaded')  # uploaded, processed, cleaned, error
    error_message = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Dataset {self.filename}>'

    def to_dict(self):
        return {
            'id': self.id,
            'survey_id': self.survey_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'total_rows': self.total_rows,
            'total_columns': self.total_columns,
            'schema_info': self.schema_info,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
