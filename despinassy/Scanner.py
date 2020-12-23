from despinassy.db import db
import datetime


class Scanner(db.Model):
    __tablename__ = 'scanner'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Integer)
    name = db.Column(db.String(50))
    redis = db.Column(db.String(50))
    settings = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return "<Scanner id=%i name='%s' redis='%s' settings='%s'>" % (
            self.id, self.name, self.redis, self.settings)
