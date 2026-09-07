from datetime import datetime
from app import db


class GenericEvaluation(db.Model):
    __tablename__ = 'generic_evaluations'

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(120), nullable=False, default='')
    metodo = db.Column(db.String(80), nullable=False)
    trabajador = db.Column(db.String(180), nullable=False, default='')
    puesto = db.Column(db.String(180), nullable=False, default='')
    fecha = db.Column(db.String(32), nullable=True)
    final_score = db.Column(db.Integer, nullable=True)
    risk_level = db.Column(db.String(120), nullable=True)
    payload_json = db.Column(db.Text, nullable=False, default='{}')
    result_json = db.Column(db.Text, nullable=False, default='{}')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
