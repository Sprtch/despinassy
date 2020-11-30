from despinassy.db import db
from sqlalchemy.orm import relationship, backref
import csv
import datetime

class Inventory(db.Model):
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    counter = db.Column(db.Integer, default=0)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), unique=True)
    part = relationship('Part')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return "<Inventory id=%i count=%i barcode='%s'>" % (self.id, self.counter, self.part.barcode)

    def add(self, number=1):
        self.counter += number

    def to_dict(self):
        return {
            'id': self.id,
            'part': self.part.to_dict(),
            'counter': self.counter,
        }

    @staticmethod
    def export_csv():
        pass # TODO
