
"""
Report Model - Stores generated reports
"""
from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)

    # Report information
    report_name = db.Column(db.String(200), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # pdf, html, excel
    template_used = db.Column(db.String(100))

    # File information
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)

    # Report configuration
    report_config = db.Column(JSON, default={})  # Configuration used to generate report

    # Report content metadata
    sections_included = db.Column(JSON, default=[])  # List of report sections
    statistics_included = db.Column(JSON, default={})  # Summary of statistics included

    # Generation status
    status = db.Column(db.String(50), default='generating')  # generating, completed, error
    error_message = db.Column(db.Text)
    generation_time = db.Column(db.Float)  # Time taken to generate in seconds

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Report {self.report_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'survey_id': self.survey_id,
            'dataset_id': self.dataset_id,
            'report_name': self.report_name,
            'report_type': self.report_type,
            'template_used': self.template_used,
            'filename': self.filename,
            'file_size': self.file_size,
            'report_config': self.report_config,
            'sections_included': self.sections_included,
            'statistics_included': self.statistics_included,
            'status': self.status,
            'error_message': self.error_message,
            'generation_time': self.generation_time,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
