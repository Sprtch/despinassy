from despinassy.db import db
from despinassy.ipc import IpcOrigin, IpcMessageType
from despinassy.Channel import Channel
from sqlalchemy.orm import relationship, validates
from sqlalchemy.exc import IntegrityError
from enum import IntEnum
import datetime
import json


class PrinterDialectEnum(IntEnum):
    """
    List the currently supported printer dialect for printer device to output.
    """

    UNDEFINED = 0
    """Not defined dialect"""
    ZEBRA_ZPL = 1
    """The Zebra ZPL printing language"""
    TEST_JSON = 2
    """Output as JSON object"""

    @staticmethod
    def from_extension(extension: str):
        """Return dialect from file extension.

        :param extension: String representing the extension of the dialect.
        """
        if extension == "zpl":
            return PrinterDialectEnum.ZEBRA_ZPL
        elif extension == "json":
            return PrinterDialectEnum.TEST_JSON
        else:
            return PrinterDialectEnum.UNDEFINED


class PrinterTypeEnum(IntEnum):
    """
    List the currently supported type of printer device.
    """

    UNDEFINED = 0
    """Not defined printer"""
    STDOUT = 1
    """Print to the terminal"""
    TEST = 2
    """Printer type used only on test case"""
    STATIC = 3
    """Network printer with a static IP address"""


class Printer(db.Model):
    """
    The `Printer` model code.

    Printers entry are devices that can output parts in a defined dialect.
    This model holds the information about this output device.
    A `Printer` can either be something virtual that will just output the
    result to a console or a physical device like a Zebra sticker printer.
    """

    __tablename__ = "printer"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    type = db.Column(db.Enum(PrinterTypeEnum), nullable=False)
    """
    Type of printer device. See :class:`despinassy.Printer.PrinterTypeEnum` for
    more information.
    """

    available = db.Column(db.Boolean)
    """
    Whether or not the `Printer` is currently available to print something.
    For instance if a printer of type `PrinterTypeEnum.STATIC` is not connected
    this boolean will be listed as false.
    """

    width = db.Column(db.Integer)
    """Width of the output"""
    height = db.Column(db.Integer)
    """Height of the output"""

    dialect = db.Column(db.Enum(PrinterDialectEnum), nullable=False)
    """
    Print form of the output of the printer.
    See :class:`despinassy.Printer.PrinterDialectEnum` for more information.
    """

    name = db.Column(db.String(50), nullable=False)
    """User defined common name for this printer"""

    redis_id = db.Column(db.Integer, db.ForeignKey("channel.id"))
    redis = relationship("Channel")
    """Channel the printer listen for incoming message"""

    settings = db.Column(db.JSON)
    """Settings dependant on printer type"""

    transactions = relationship(
        "PrinterTransaction",
        order_by="desc(PrinterTransaction.created_at)",
        back_populates="printer",
    )
    """List of transaction sent to this printer"""

    hidden = db.Column(db.Boolean, default=False)
    """Is the printer hidden to the user."""

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
        """Helper to create a new :class:`despinassy.Printer.PrinterTransaction`

        Someone should always use this helper function to create a new
        :class:`despinassy.Printer.PrinterTransaction` instead of creating
        one by hand.
        """
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
    """
    The `PrinterTransaction` model code representing the messages sent
    to a :class:`despinassy.Printer.Printer`.

    The transaction of a printer can either be control messages or print query
    to output content like parts from the printer.
    """

    __tablename__ = "printer_transaction"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    printer_id = db.Column(db.Integer, db.ForeignKey("printer.id"))
    printer = relationship("Printer")
    """:class:`despinassy.Printer.Printer` where the transaction happened"""

    # part_id = db.Column(db.Integer, db.ForeignKey('part.id'), unique=True)
    # part = relationship('Part')

    destination = db.Column(db.String(50))

    origin = db.Column(db.Enum(IpcOrigin), nullable=False)
    """
    Device that created this transaction.
    See :class:`despinassy.ipc.IpcOrigin` for more information.
    """

    device = db.Column(db.String(50))
    """
    String precising the origin of the originator of the transaction.
    """

    msg_type = db.Column(db.Integer, default=IpcMessageType.PRINT)
    """
    Type of the message received by the printer.
    See :class:`despinassy.ipc.IpcOrigin` for more information.
    """

    barcode = db.Column(db.String(50), nullable=False)
    """Barcode of the part the message refer to"""

    name = db.Column(db.String(120), nullable=False)
    """Name of the part the message refer to"""

    number = db.Column(db.Integer, default=1)
    """Number of output required by the printer"""

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
