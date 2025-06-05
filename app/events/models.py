from app import db
from sqlalchemy.dialects.postgresql import JSONB
import uuid

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    aggregate_id = db.Column(db.String(36), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    event_data = db.Column(JSONB, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<Event {self.event_type} for aggregate {self.aggregate_id}>'