from despinassy.db import db
from despinassy.Part import Part
from sqlalchemy.orm import relationship, validates
import csv
import io
import datetime


class InventorySession(db.Model):
    __tablename__ = "inventory_session"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    entries = relationship("Inventory", back_populates="session")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "created_at": self.created_at}


class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quantity = db.Column(db.Integer, default=0)
    part_id = db.Column(db.Integer, db.ForeignKey("part.id"))
    part = relationship("Part")
    session_id = db.Column(db.Integer, db.ForeignKey("inventory_session.id"))
    session = relationship("InventorySession")
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
        }

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
            "created_at",
            "updated_at",
        ]
        writer = csv.DictWriter(
            strio, fieldnames=columns, delimiter=delimiter, lineterminator="\n"
        )
        writer.writeheader()
        for i in Inventory.query.all():
            row = {
                "id": i.id,
                "part_name": i.part.name,
                "part_barcode": i.part.barcode,
                "quantity": i.quantity,
                "created_at": str(i.created_at),
                "updated_at": str(i.updated_at),
            }
            writer.writerow(row)

        return strio

    @staticmethod
    def export_csv(path):
        with open(path, "w") as csvfile:
            csvfile.write(Inventory._export_csv().getvalue())
