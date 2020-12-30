from despinassy.db import db
from enum import IntEnum
import datetime
import json


class ScannerTypeEnum(IntEnum):
    UNDEFINED = 0
    STDIN = 1
    TEST = 2
    SERIAL = 3
    EVDEV = 4


class Scanner(db.Model):
    __tablename__ = 'scanner'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Enum(ScannerTypeEnum), nullable=False)
    name = db.Column(db.String(50))
    redis = db.Column(db.String(50))
    settings = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'name': self.name,
            'redis': self.redis,
            'settings': json.loads(self.settings),
        }

    def __repr__(self):
        return "<Scanner id=%i type=%i name='%s' redis='%s' settings='%s'>" % (
            self.id, self.type, self.name, self.redis, self.settings)
