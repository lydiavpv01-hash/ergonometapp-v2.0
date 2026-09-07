from datetime import datetime
from app import db


class RebaEvaluation(db.Model):
    __tablename__ = 'reba_evaluations'

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(120), nullable=False, default='')
    trabajador = db.Column(db.String(180), nullable=False, default='')
    puesto = db.Column(db.String(180), nullable=False, default='')
    area = db.Column(db.String(180), nullable=True)
    tarea = db.Column(db.String(255), nullable=True)
    evaluador = db.Column(db.String(180), nullable=True)
    fecha = db.Column(db.String(32), nullable=True)
    score_a = db.Column(db.Integer, nullable=True)
    score_b = db.Column(db.Integer, nullable=True)
    score_c = db.Column(db.Integer, nullable=True)
    activity_score = db.Column(db.Integer, nullable=True)
    final_score = db.Column(db.Integer, nullable=True)
    risk_level = db.Column(db.String(120), nullable=True)
    payload_json = db.Column(db.Text, nullable=False)
    result_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
