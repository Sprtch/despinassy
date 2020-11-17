from despinassy.db import db
from sqlalchemy.orm import relationship, backref
from sqlalchemy import inspect
import csv
import io
import os

class Part(db.Model):
    __tablename__ = 'part'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    barcode = db.Column(db.String(120), index=True, unique=True)
    name = db.Column(db.String(50))
    counter = db.Column(db.Integer, default=0)
    inventories = relationship('Inventory', back_populates='part')

    def __repr__(self):
        return '<Part %r:%r>' % (self.name, self.barcode)

    def printed(self):
        self.counter += 1

    def to_dict(self):
        return {
            'id': self.id,
            'barcode': self.barcode,
            'name': self.name,
            'counter': self.counter,
        }

    @staticmethod
    def _import_csv_content(strio: io.TextIOWrapper, csv_map=None, delimiter=",", **kwargs):
        csv_reader = csv.DictReader(strio, delimiter=delimiter, **kwargs)

        if csv_map is None:
            csv_map = {}
            for column in inspect(Part).columns.keys():
                if column in csv_reader.fieldnames:
                    csv_map[column] = column
        
        Part.query.delete() # Completely remove every entry in Part.
        for i, row in enumerate(csv_reader):
            if i > 0 and all([row[x] for x in csv_map.keys()]):
                args = {}
                for x in csv_map.keys():
                    args[csv_map[x]] = row[x]

                db.session.add(Part(**args))
                try:
                    db.session.commit()
                except:
                    db.session.rollback()

    @staticmethod
    def import_csv(filename, csv_map=None):
        if not os.path.exists(filename):
            raise FileNotFoundError

        with open(filename, mode="r", encoding="ISO-8859-1", errors='ignore') as csv_file:
            Part._import_csv_content(csv_file, csv_map)
