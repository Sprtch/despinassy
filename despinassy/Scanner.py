from despinassy.db import db
from despinassy.Channel import Channel
from sqlalchemy.orm import relationship, validates
from sqlalchemy.exc import IntegrityError
from sqlalchemy import event
from enum import IntEnum
import datetime
import json


class ScannerTypeEnum(IntEnum):
    """
    List the currently supported type of scanner device.
    """

    UNDEFINED = 0
    """Undefined scanner"""
    STDIN = 1
    """Input from stdin"""
    TEST = 2
    """Scanner used in tests"""
    SERIAL = 3
    """Serial device scanner"""
    EVDEV = 4
    """Usb device scanner"""
    HURON = 5
    """Input from the huron webapp"""


class ScannerModeEnum(IntEnum):
    """
    List supported mode for scanners.
    """

    UNDEFINED = 0
    """Undefined mode"""
    PRINTMODE = 1
    """Print mode, scanning a barcode will print it"""
    INVENTORYMODE = 2
    """Inventory mode, scanning a barcode will add an entry to the inventory"""


class Scanner(db.Model):
    """
    The `Scanner` model code.

    Scanners are devices that can input/scan barcodes.
    Scanners can be physical device (USB, bluetooth) or virtual like the input
    from STDIN or the input from a webapp.
    """

    __tablename__ = "scanner"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Enum(ScannerTypeEnum), nullable=False)
    """
    Type of scanner device. See :class:`despinassy.Scanner.ScannerTypeEnum` for
    more information.
    """

    mode = db.Column(
        db.Enum(ScannerModeEnum), default=ScannerModeEnum.PRINTMODE, nullable=False
    )
    """
    Current mode of the scanner device.
    See :class:`despinassy.Scanner.ScannerModeEnum` for more information.
    """

    available = db.Column(db.Boolean)
    """
    Whether or not the `Scanner` is currently available to scan.
    For instance if a usb scanner is disconnected this boolean will be 
    set to false.
    """

    name = db.Column(db.String(50), unique=True)
    """User defined common name for this scanner"""

    redis_id = db.Column(db.Integer, db.ForeignKey("channel.id"))
    redis = relationship("Channel")
    """Channel the scanner send message to"""

    settings = db.Column(db.JSON)
    """Settings dependant on scanner type"""

    transactions = relationship(
        "ScannerTransaction",
        order_by="desc(ScannerTransaction.created_at)",
        back_populates="scanner",
    )
    """List of transaction made by this scanner"""

    hidden = db.Column(db.Boolean, default=False)
    """Is the scanner hidden to the user."""

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    @validates("redis")
    def validate_redis(self, key, value):
        if isinstance(value, str):
            c = Channel.query.filter_by(name=value).first()
            if c is None:
                try:
                    c = Channel(name=value)
                    db.session.add(c)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    c = Channel.query.filter(Channel.name == value).first()
        elif isinstance(value, Channel):
            c = value
        else:
            raise Exception("Not valid redis")

        return c

    def to_dict(self, full=False):
        if full:
            return {
                "id": self.id,
                "type": self.type,
                "name": self.name,
                "redis": str(self.redis),
                "settings": json.loads(self.settings),
                "mode": self.mode,
                "available": self.available,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "transactions": [t.to_dict() for t in self.transactions],
                "hidden": self.hidden,
            }
        else:
            return {
                "id": self.id,
                "type": self.type,
                "name": self.name,
                "redis": str(self.redis),
                "settings": json.loads(self.settings),
                "mode": self.mode,
                "available": self.available,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "hidden": self.hidden,
            }

    def add_transaction(self, **kwargs):
        """Helper to create a new :class:`despinassy.Scanner.ScannerTransaction`

        Always use this helper function to create a new
        :class:`despinassy.Scanner.ScannerTransaction` instead of creating
        one by hand.
        """

        self.updated_at = datetime.datetime.utcnow()
        st = ScannerTransaction(scanner=self, **kwargs)
        return st

    def __repr__(self):
        return "<Scanner id=%i type=%i name='%s' redis='%s' settings='%s'>" % (
            self.id,
            self.type,
            self.name,
            str(self.redis),
            self.settings,
        )


class ScannerTransaction(db.Model):
    """
    The `ScannerTransaction` model code representing the messages sent
    by the :class:`despinassy.Scanner.Scanner`.
    """

    __tablename__ = "scanner_transaction"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    scanner_id = db.Column(db.Integer, db.ForeignKey("scanner.id"))
    scanner = relationship("Scanner")
    """:class:`despinassy.Scanner.Scanner` origin of the transaction"""

    mode = db.Column(db.Enum(ScannerModeEnum), nullable=False)
    """
    Mode of the :class:`despinassy.Scanner.Scanner` at the moment of the
    transaction
    """

    quantity = db.Column(db.Float, default=1)
    """Quantity attached to the value logged by this transaction"""

    value = db.Column(db.String(50), nullable=False)
    """Input or scanned value"""

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self, full=False):
        if full:
            return {
                "id": self.id,
                "scanner": self.scanner_id,
                "mode": int(self.mode),
                "quantity": self.quantity,
                "value": self.value,
                "created_at": self.created_at,
            }
        else:
            return {
                "id": self.id,
                "mode": int(self.mode),
                "quantity": self.quantity,
                "value": self.value,
                "created_at": self.created_at,
            }
