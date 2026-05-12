from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Link(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    original    = db.Column(db.Text, nullable=False)
    short_code  = db.Column(db.String(8), unique=True, nullable=False)
    clicks      = db.Column(db.Integer, default=0)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":         self.id,
            "original":   self.original,
            "short_code": self.short_code,
            "clicks":     self.clicks,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
        }
