from despinassy.db import db
from sqlalchemy.orm import relationship
from sqlalchemy import inspect
from sqlalchemy.orm import validates
from sqlalchemy.exc import ArgumentError
import datetime
import csv
import io
import os


class Part(db.Model):
    __tablename__ = "part"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    barcode = db.Column(db.String(128), unique=True, index=True)
    name = db.Column(db.String(128))
    counter = db.Column(db.Integer, default=0)
    inventories = relationship(
        "Inventory",
        back_populates="part",
        passive_deletes="ALL",
    )
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    @validates("barcode")
    def validate_barcode(self, key, value):
        max_len = getattr(self.__class__, key).prop.columns[0].type.length
        if value and len(value) > max_len:
            raise ArgumentError('"barcode" value is too long')
        return value

    @validates("name")
    def validate_name(self, key, value):
        max_len = getattr(self.__class__, key).prop.columns[0].type.length
        if value and len(value) > max_len:
            return value[:max_len]
        return value

    def __repr__(self):
        return "<Part %r:%r>" % (self.name, self.barcode)

    def printed(self, number=1):
        self.counter += number

    def to_dict(self):
        return {
            "id": self.id,
            "barcode": self.barcode,
            "name": self.name,
            "counter": self.counter,
        }

    @staticmethod
    def _import_csv_content(
        strio: io.TextIOWrapper, csv_map=None, delimiter=",", **kwargs
    ):
        csv_reader = csv.DictReader(strio, delimiter=delimiter, **kwargs)

        if csv_map is None:
            csv_map = {}
            for column in inspect(Part).columns.keys():
                if column in csv_reader.fieldnames:
                    csv_map[column] = column

        Part.query.delete()  # Completely remove every entry in Part.
        parts = []
        for row in csv_reader:
            args = {}
            for x in csv_map.keys():
                max_len = getattr(Part, x).prop.columns[0].type.length
                content = row[csv_map[x]]
                if len(content) > max_len:
                    content = content[:max_len]
                args[x] = content

            if all([args[x] for x in args]):
                parts.append(args)
            else:
                # Do not import row with empty fields
                continue

        db.session.bulk_insert_mappings(Part, parts)
        db.session.commit()

    @staticmethod
    def import_csv(filename, csv_map=None, encoding="latin1"):
        if not os.path.exists(filename):
            raise FileNotFoundError

        with open(filename, mode="r", encoding=encoding, errors="ignore") as csv_file:
            Part._import_csv_content(csv_file, csv_map)
