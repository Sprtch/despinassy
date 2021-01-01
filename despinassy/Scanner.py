from despinassy.db import db
from sqlalchemy.orm import relationship
from enum import IntEnum
import datetime
import json


class ScannerTypeEnum(IntEnum):
    UNDEFINED = 0
    STDIN = 1
    TEST = 2
    SERIAL = 3
    EVDEV = 4


class ScannerModeEnum(IntEnum):
    UNDEFINED = 0
    PRINTMODE = 1
    INVENTORYMODE = 2


class Scanner(db.Model):
    __tablename__ = 'scanner'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Enum(ScannerTypeEnum), nullable=False)
    mode = db.Column(db.Enum(ScannerModeEnum),
                     default=ScannerModeEnum.PRINTMODE,
                     nullable=False)
    available = db.Column(db.Boolean)
    name = db.Column(db.String(50))
    redis = db.Column(db.String(50))
    settings = db.Column(db.JSON)
    transactions = relationship('ScannerTransaction', back_populates='scanner')

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    def to_dict(self, full=False):
        if full:
            return {
                'id': self.id,
                'type': self.type,
                'name': self.name,
                'redis': self.redis,
                'available': self.available,
                'settings': json.loads(self.settings),
                'transactions': [t.to_dict() for t in self.transactions],
                'created_at': self.created_at,
                'updated_at': self.updated_at,
            }
        else:
            return {
                'id': self.id,
                'type': self.type,
                'mode': self.mode,
                'available': self.available,
                'name': self.name,
                'redis': self.redis,
            }

    def add_transaction(self, **kwargs):
        st = ScannerTransaction(scanner=self, **kwargs)
        return st

    def __repr__(self):
        return "<Scanner id=%i type=%i name='%s' redis='%s' settings='%s'>" % (
            self.id, self.type, self.name, self.redis, self.settings)


class ScannerTransaction(db.Model):
    __tablename__ = 'scanner_transaction'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scanner_id = db.Column(db.Integer, db.ForeignKey('scanner.id'))
    scanner = relationship('Scanner')
    mode = db.Column(db.Enum(ScannerModeEnum), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    value = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'mode': int(self.mode),
            'quantity': self.quantity,
            'value': self.value,
            'created_at': self.created_at,
        }
