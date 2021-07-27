from despinassy.db import db
from sqlalchemy.orm import relationship
import datetime


class Channel(db.Model):
    __tablename__ = "channel"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), unique=True, index=True)
    printers = relationship("Printer", back_populates="redis")
    scanners = relationship("Scanner", back_populates="redis")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return "<Channel %r>" % (self.name)

    def __print__(self):
        return self.name

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }
