from datetime import datetime
from app import db


class EvaluationUpload(db.Model):
    __tablename__ = 'evaluation_uploads'

    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('generic_evaluations.id'), nullable=False, index=True)
    usuario = db.Column(db.String(120), nullable=False, default='', index=True)
    field = db.Column(db.String(180), nullable=False, default='archivo')
    name = db.Column(db.String(255), nullable=False, default='imagen.jpg')
    mime_type = db.Column(db.String(100), nullable=False, default='image/jpeg')
    size = db.Column(db.Integer, nullable=True)
    data = db.Column(db.Text, nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def as_payload(self):
        return {
            'field': self.field,
            'name': self.name,
            'type': self.mime_type,
            'size': self.size or 0,
            'data': self.data,
            'position': self.position,
        }
