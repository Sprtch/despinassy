from despinassy.db import db
from sqlalchemy.orm import relationship, backref

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
