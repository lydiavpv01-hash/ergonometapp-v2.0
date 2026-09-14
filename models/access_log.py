from datetime import datetime
from app import db


class AccessLog(db.Model):
    __tablename__ = 'access_logs'

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(180), nullable=False, index=True)
    logged_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
