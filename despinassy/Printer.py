from despinassy.db import db
from sqlalchemy.orm import relationship
from enum import IntEnum
import datetime
import json


class PrinterDialectEnum(IntEnum):
    UNDEFINED = 0
    ZEBRA_ZPL = 1
    TEST_JSON = 2

    @staticmethod
    def from_extension(extension: str):
        if extension == "zpl":
            return PrinterDialectEnum.ZEBRA_ZPL
        elif extension == "json":
            return PrinterDialectEnum.TEST_JSON
        else:
            return PrinterDialectEnum.UNDEFINED


class PrinterTypeEnum(IntEnum):
    UNDEFINED = 0
    STDOUT = 1
    TEST = 2
    STATIC = 3


class Printer(db.Model):
    __tablename__ = 'printer'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Enum(PrinterTypeEnum), nullable=False)
    available = db.Column(db.Boolean)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    dialect = db.Column(db.Enum(PrinterDialectEnum), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    redis = db.Column(db.String(50))
    settings = db.Column(db.JSON)
    transactions = relationship('PrinterTransaction', back_populates='printer')

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'width': self.width,
            'height': self.height,
            'dialect': self.dialect,
            'name': self.name,
            'redis': self.redis,
            'settings': json.loads(self.settings),
        }

    def __repr__(self):
        return "<Printer id=%i type=%i name='%s' redis='%s' settings='%s'>" % (
            self.id, self.type, self.name, self.redis, self.settings)


class PrinterTransaction(db.Model):
    __tablename__ = 'printer_transaction'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    printer_id = db.Column(db.Integer,
                           db.ForeignKey('printer.id'),
                           unique=True)
    printer = relationship('Printer')
    value = db.Column(db.String(50))
