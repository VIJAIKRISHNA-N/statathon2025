
"""
Cleaning Configuration Model - Stores data cleaning settings
"""
from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class CleaningConfig(db.Model):
    __tablename__ = 'cleaning_configs'

    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)

    # Cleaning configuration
    config_name = db.Column(db.String(200), nullable=False)

    # Imputation settings
    imputation_method = db.Column(db.String(50), default='mean')  # mean, median, mode, knn, forward_fill
    imputation_columns = db.Column(JSON, default=[])  # List of columns to apply imputation

    # Outlier detection settings
    outlier_method = db.Column(db.String(50), default='z_score')  # z_score, iqr, isolation_forest, lof
    outlier_threshold = db.Column(db.Float, default=3.0)
    outlier_columns = db.Column(JSON, default=[])  # List of columns to check for outliers
    outlier_action = db.Column(db.String(20), default='remove')  # remove, cap, flag

    # Validation rules
    validation_rules = db.Column(JSON, default={})  # Custom validation rules

    # Processing results
    is_applied = db.Column(db.Boolean, default=False)
    applied_at = db.Column(db.DateTime)
    results = db.Column(JSON, default={})  # Results of cleaning operations

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<CleaningConfig {self.config_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'survey_id': self.survey_id,
            'dataset_id': self.dataset_id,
            'config_name': self.config_name,
            'imputation_method': self.imputation_method,
            'imputation_columns': self.imputation_columns,
            'outlier_method': self.outlier_method,
            'outlier_threshold': self.outlier_threshold,
            'outlier_columns': self.outlier_columns,
            'outlier_action': self.outlier_action,
            'validation_rules': self.validation_rules,
            'is_applied': self.is_applied,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'results': self.results,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
