
"""
Weight Configuration Model - Stores survey weighting settings
"""
from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class WeightConfig(db.Model):
    __tablename__ = 'weight_configs'

    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)

    # Weight configuration
    config_name = db.Column(db.String(200), nullable=False)

    # Design weights
    design_weight_column = db.Column(db.String(100))  # Column containing design weights
    design_weight_method = db.Column(db.String(50), default='inverse_probability')

    # Population weights
    population_targets = db.Column(JSON, default={})  # Target population proportions
    stratification_vars = db.Column(JSON, default=[])  # Variables for stratification

    # Calibration settings
    calibration_method = db.Column(db.String(50), default='raking')  # raking, post_stratification
    calibration_tolerance = db.Column(db.Float, default=0.01)
    max_iterations = db.Column(db.Integer, default=100)

    # Weight trimming
    trim_weights = db.Column(db.Boolean, default=False)
    trim_lower = db.Column(db.Float, default=0.1)
    trim_upper = db.Column(db.Float, default=10.0)

    # Processing results
    is_applied = db.Column(db.Boolean, default=False)
    applied_at = db.Column(db.DateTime)
    weight_summary = db.Column(JSON, default={})  # Summary statistics of weights

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<WeightConfig {self.config_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'survey_id': self.survey_id,
            'dataset_id': self.dataset_id,
            'config_name': self.config_name,
            'design_weight_column': self.design_weight_column,
            'design_weight_method': self.design_weight_method,
            'population_targets': self.population_targets,
            'stratification_vars': self.stratification_vars,
            'calibration_method': self.calibration_method,
            'calibration_tolerance': self.calibration_tolerance,
            'max_iterations': self.max_iterations,
            'trim_weights': self.trim_weights,
            'trim_lower': self.trim_lower,
            'trim_upper': self.trim_upper,
            'is_applied': self.is_applied,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'weight_summary': self.weight_summary,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
