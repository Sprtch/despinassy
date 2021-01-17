from despinassy.db import db
from despinassy.Channel import Channel
from sqlalchemy.orm import relationship, validates
from enum import IntEnum
import datetime
import json


class ScannerTypeEnum(IntEnum):
    UNDEFINED = 0
    STDIN = 1
    TEST = 2
    SERIAL = 3
    EVDEV = 4
    HURON = 5


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
    name = db.Column(db.String(50), unique=True)
    redis_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
    redis = relationship('Channel')
    settings = db.Column(db.JSON)
    transactions = relationship('ScannerTransaction', back_populates='scanner')

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    @validates('redis')
    def validate_redis(self, key, value):
        c = Channel.query.filter(Channel.name == value)
        if c.count():
            c = c.first()
        else:
            c = Channel(name=value)
            db.session.add(c)
            db.session.commit()
        return c

    def to_dict(self, full=False):
        if full:
            return {
                'id': self.id,
                'type': self.type,
                'name': self.name,
                'redis': str(self.redis),
                'settings': json.loads(self.settings),
                'mode': self.mode,
                'available': self.available,
                'created_at': self.created_at,
                'updated_at': self.updated_at,
                'transactions': [t.to_dict() for t in self.transactions],
            }
        else:
            return {
                'id': self.id,
                'type': self.type,
                'name': self.name,
                'redis': str(self.redis),
                'settings': json.loads(self.settings),
                'mode': self.mode,
                'available': self.available,
                'created_at': self.created_at,
                'updated_at': self.updated_at,
            }

    def add_transaction(self, **kwargs):
        self.updated_at = datetime.datetime.utcnow()
        st = ScannerTransaction(scanner=self, **kwargs)
        return st

    def __repr__(self):
        return "<Scanner id=%i type=%i name='%s' redis='%s' settings='%s'>" % (
            self.id, self.type, self.name, str(self.redis), self.settings)


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
