from despinassy.db import db
from despinassy.ipc import IpcOrigin, IpcMessageType
from despinassy.Channel import Channel
from sqlalchemy.orm import relationship, validates
from sqlalchemy.exc import IntegrityError
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
    __tablename__ = "printer"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Enum(PrinterTypeEnum), nullable=False)
    available = db.Column(db.Boolean)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    dialect = db.Column(db.Enum(PrinterDialectEnum), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    redis_id = db.Column(db.Integer, db.ForeignKey("channel.id"))
    redis = relationship("Channel")
    settings = db.Column(db.JSON)
    transactions = relationship(
        "PrinterTransaction",
        order_by="desc(PrinterTransaction.created_at)",
        back_populates="printer",
    )

    hidden = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    @validates("redis")
    def validate_redis(self, key, value):
        c = Channel.query.filter(Channel.name == value)
        if c.count():
            c = c.first()
        else:
            try:
                c = Channel(name=value)
                db.session.add(c)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                c = Channel.query.filter(Channel.name == value).first()
        return c

    def to_dict(self, full=False):
        if full:
            return {
                "id": self.id,
                "type": self.type,
                "available": self.available,
                "width": self.width,
                "height": self.height,
                "dialect": self.dialect,
                "name": self.name,
                "redis": str(self.redis),
                "settings": json.loads(self.settings),
                "transactions": [t.to_dict() for t in self.transactions],
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "hidden": self.hidden,
            }
        else:
            return {
                "id": self.id,
                "type": self.type,
                "available": self.available,
                "width": self.width,
                "height": self.height,
                "dialect": self.dialect,
                "name": self.name,
                "redis": str(self.redis),
                "settings": json.loads(self.settings),
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "hidden": self.hidden,
            }

    def add_transaction(self, **kwargs):
        self.updated_at = datetime.datetime.utcnow()
        pt = PrinterTransaction(printer=self, **kwargs)
        return pt

    def __repr__(self):
        return "<Printer id=%i type=%i name='%s' redis='%s' settings='%s'>" % (
            self.id,
            self.type,
            self.name,
            str(self.redis),
            self.settings,
        )


class PrinterTransaction(db.Model):
    __tablename__ = "printer_transaction"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    printer_id = db.Column(db.Integer, db.ForeignKey("printer.id"))
    printer = relationship("Printer")
    # part_id = db.Column(db.Integer, db.ForeignKey('part.id'), unique=True)
    # part = relationship('Part')
    destination = db.Column(db.String(50))
    origin = db.Column(db.Enum(IpcOrigin), nullable=False)
    msg_type = db.Column(db.Integer, default=IpcMessageType.PRINT)
    device = db.Column(db.String(50))
    barcode = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    number = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "barcode": self.barcode,
            "name": self.name,
            "number": self.number,
            "origin": self.origin,
            "device": self.device,
            "created_at": self.created_at,
        }
