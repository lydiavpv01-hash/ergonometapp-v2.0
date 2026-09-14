from datetime import datetime
from app import db


class RevokedUser(db.Model):
    __tablename__ = 'revoked_users'

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(180), unique=True, nullable=False, index=True)
    revoked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
