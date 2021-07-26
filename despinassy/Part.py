from despinassy.db import db
from sqlalchemy.orm import relationship
from sqlalchemy import inspect
from sqlalchemy.orm import validates
from sqlalchemy.exc import ArgumentError
from sqlalchemy import tuple_
from sqlalchemy.sql import and_, or_
import datetime
import csv
import io
import os


class Part(db.Model):
    """
    The `Part` model code.

    Each part get associated with a unique `barcode` and a familiar `name`.
    """

    __tablename__ = "part"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    barcode = db.Column(db.String(128), unique=True, index=True)
    """Unique barcode representation of the part"""

    name = db.Column(db.String(128))
    """Familiar name of the part"""

    counter = db.Column(db.Integer, default=0)
    """Count of the number of time the `Part` has been printed"""

    inventories = relationship(
        "Inventory",
        back_populates="part",
        passive_deletes="ALL",
    )
    """
    List of related inventory entries for this part.
    See :class:`despinassy.Inventory` for more information about inventory.

    More than one entry can exist for the same part for different
    :class:`despinassy.InventorySession`.
    """

    hidden = db.Column(db.Boolean, default=False)
    """
    Is the part hidden.

    This is used to differentiate the currently in use parts from the one that
    got deleted without having to delete the :class:`despinassy.Inventory`
    entry related to this part.

    This boolean value allow API to list all the existing non hidden parts
    easily.
    """

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
        def _get_column_max_len(col):
            # TODO verify column is of string type
            return getattr(Part, col).prop.columns[0].type.length

        def _truncate_column_content(column, content):
            max_len = _get_column_max_len(column)
            if len(content) > max_len:
                return content[:max_len]
            return content

        csv_reader = csv.DictReader(strio, delimiter=delimiter, **kwargs)

        if csv_map is None:
            # if no csv_map use the column with matching name.
            csv_map = {}
            for column in inspect(Part).columns.keys():
                if column in csv_reader.fieldnames:
                    csv_map[column] = column

        if ("name" not in csv_map) or ("barcode" not in csv_map):
            # TODO Log error
            return

        # TODO For now only importing 'name' and 'barcode' is supported
        _col_name = csv_map["name"]
        _col_barcode = csv_map["barcode"]
        tuple_parts = {
            (x[_col_name], x[_col_barcode])
            for x in csv_reader
            if x.get(_col_name) and x.get(_col_barcode)
        }

        # retrieve the 'parts' present in the db and in the '.csv'
        # cond = tuple_(Part.name, Part.barcode).in_(list(tuple_parts)) # TODO if postgres
        cond = or_(*(and_(Part.name == x, Part.barcode == y) for (x, y) in tuple_parts))
        in_db = Part.query.filter(cond)
        in_db.update({"hidden": False})

        to_remove = Part.query.filter(~cond)
        to_remove.update({"hidden": True})

        if in_db.count() > 0:
            # TODO add the part
            tuple_parts = tuple_parts - {(x.name, x.barcode) for x in in_db.all()}

        parts = [
            {
                "name": _truncate_column_content("name", name),
                "barcode": _truncate_column_content("barcode", barcode),
            }
            for (name, barcode) in tuple_parts
        ]

        db.session.bulk_insert_mappings(Part, parts)
        db.session.commit()

    @staticmethod
    def import_csv(filename, csv_map=None, encoding="latin1"):
        """Perform a mass import of a '.csv' file containing parts.

        :param filename: The location of the '.csv' file that containing the
         parts.  This '.csv' file will be read and should contain a list of
         parts with a header containing the name of the column.

        :param csv_map: dictionary containing the name of the
         :class:`despinassy.Part` column as key and the name of the '.csv'
         header column name as attribute.  This argument is also used to select
         the column of the '.csv' that will be imported. If no csv_map is
         provided the function will assume the '.csv' header thath match a
         column name present in the :class:`despinassy.Part` table will be
         used.

        :param encoding: The encoding of the filename that will be read.
         The encoding 'latin1' is used by default.
        """
        if not os.path.exists(filename):
            raise FileNotFoundError

        with open(filename, mode="r", encoding=encoding, errors="ignore") as csv_file:
            Part._import_csv_content(csv_file, csv_map)
