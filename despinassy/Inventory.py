from despinassy.db import db
from despinassy.Part import Part
from sqlalchemy.orm import relationship, validates
from enum import IntEnum
import csv
import io
import datetime


class InventoryUnitEnum(IntEnum):
    UNDEFINED = 0
    PIECES = 1
    METER = 2
    SQUARE_METER = 3

    def __str__(self):
        if self.value == InventoryUnitEnum.UNDEFINED:
            return "undefined"
        elif self.value == InventoryUnitEnum.PIECES:
            return "pcs"
        elif self.value == InventoryUnitEnum.METER:
            return "m"
        elif self.value == InventoryUnitEnum.SQUARE_METER:
            return "m³"

    def __repr__(self):
        return str(self)


class InventorySession(db.Model):
    """
    InventorySession is the representation of inventory at a certain moment.

    Typically inventories at warehouse are done at regular intervals. During
    an inventory session the current stock for each part in the warehouse get
    logged. Those inventory sessions are used to re-count the stock in case
    some stock movement didn't get logged in the system correctly.

    The creation of a new InventorySession will restart all the previous
    inventory listing done in the past but not delete them.
    New Inventory are always associated to the most recent InventorySession.
    """

    __tablename__ = "inventory_session"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    entries = relationship("Inventory", back_populates="session", passive_deletes="ALL")
    """List of every inventory entry related to the session."""

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @staticmethod
    def last():
        """
        Return the last session added to the database.
        """
        return InventorySession.query.order_by(
            InventorySession.created_at.desc()
        ).first()

    def to_dict(self):
        return {"id": self.id, "created_at": self.created_at}


class Inventory(db.Model):
    """
    The Inventory model code associate a number and a unit to an existing
    :class:`despinassy.Part`.

    Inventory represent the current stock of a :class:`despinassy.Part` at
    a given time.
    """

    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    quantity = db.Column(db.Float, default=0)
    """Current quantity of a :class:`despinassy.Part` in stock"""

    unit = db.Column(db.Enum(InventoryUnitEnum), default=InventoryUnitEnum.PIECES)
    """The unit of quantity"""

    part_id = db.Column(db.Integer, db.ForeignKey("part.id", ondelete="CASCADE"))
    part = relationship("Part")
    """Part associated with this inventory entry"""

    session_id = db.Column(
        db.Integer, db.ForeignKey("inventory_session.id", ondelete="CASCADE")
    )
    session = relationship("InventorySession")
    """Session associated with this inventory entry"""

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    def __init__(self, **kwargs):
        kwargs["session"] = InventorySession.query.order_by(
            InventorySession.created_at.desc()
        ).first()
        super().__init__(**kwargs)

    def __repr__(self):
        return "<Inventory id=%i count=%i barcode='%s'>" % (
            self.id,
            self.counter,
            self.part.barcode,
        )

    def add(self, number=1):
        self.quantity += int(number)

    def to_dict(self):
        return {
            "id": self.id,
            "session": self.session_id,
            "part": self.part.to_dict(),
            "quantity": self.quantity,
            "unit": str(self.unit),
        }

    @staticmethod
    def last_session_entries():
        """
        Return the inventory entries from the last session.
        """
        last_session = InventorySession.last()
        return Inventory.query.filter(Inventory.session == last_session).all()

    @staticmethod
    def archive():
        """
        Archive the current inventory by creating a new
        :class:`despinassy.inventory.InventorySession`.
        """
        db.session.add(InventorySession())
        db.session.commit()

    @staticmethod
    def retrieve_inventory_from_barcode(barcode):
        return (
            db.session.query(Inventory)
            .join(Part)
            .filter(Part.barcode == barcode)
            .first()
        )

    @staticmethod
    def _export_csv(delimiter=","):
        strio = io.StringIO(newline=None)
        columns = [
            "id",
            "part_name",
            "part_barcode",
            "quantity",
            "unit",
            "created_at",
            "updated_at",
        ]
        writer = csv.DictWriter(
            strio, fieldnames=columns, delimiter=delimiter, lineterminator="\n"
        )
        writer.writeheader()

        for i in Inventory.last_session_entries():
            row = {
                "id": i.id,
                "part_name": i.part.name,
                "part_barcode": i.part.barcode,
                "quantity": i.quantity,
                "unit": i.unit,
                "created_at": str(i.created_at),
                "updated_at": str(i.updated_at),
            }
            writer.writerow(row)

        return strio

    @staticmethod
    def export_csv(path):
        """Export the inventory entries to a '.csv' file

        :param path: The location of the '.csv' file to save
        """
        with open(path, "w") as csvfile:
            csvfile.write(Inventory._export_csv().getvalue())
