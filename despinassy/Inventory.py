from despinassy.db import db

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    part = db.Column(db.Integer, db.ForeignKey('part.id'), unique=True)
    counter = db.Column(db.Integer, default=0)

    def __init__(self, part, barcode=None):
        self.name = name
        self.barcode = barcode
        self.counter = 0

    def __repr__(self):
        return '<Inventory %i>' % (self.id)

    def add(self, number=1):
        self.counter += number

    def to_dict(self):
        return {
            'id': self.id,
            'part': self.part.to_dict(),
            'counter': self.counter,
        }
