from sqlalchemy import orm
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model
from functools import update_wrapper

from sqlalchemy.engine import Engine
from sqlalchemy import event


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def setupmethod(f):
    def wrapper_func(self, *args, **kwargs):
        return f(self, *args, **kwargs)

    return update_wrapper(wrapper_func, f)


class NO_APP:
    extensions = {
        "sqlalchemy": None,
    }
    config = {
        "SQLALCHEMY_DATABASE_URI": None,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }
    root_path = ""

    def __init__(self, config={}):
        self.teardown_appcontext_funcs = []
        self.debug = config.setdefault("debug", False)
        NO_APP.config["SQLALCHEMY_DATABASE_URI"] = config.setdefault(
            "uri", "postgresql://postgres@localhost/sprtch"
        )

    @setupmethod
    def teardown_appcontext(self, f):
        self.teardown_appcontext_funcs.append(f)
        return f


class Despinassy(SQLAlchemy):
    def __init__(self):
        self.initialized = False
        super().__init__(
            query_class=orm.Query,
            model_class=Model,
        )

    def init_app(self, app=None, config={}):
        if self.initialized:
            return
        self.initialized = True
        if app is None:
            app = NO_APP(config)
            self.app = app
            super().init_app(app)
        else:
            super().init_app(app)

        return app

    def create_all(self):
        from despinassy.Scanner import Scanner, ScannerTypeEnum
        from despinassy.Inventory import InventorySession

        super().create_all()
        self.session.add(
            Scanner(
                type=ScannerTypeEnum.HURON,
                available=True,
                name="huron",
                redis="victoria",
                settings="{}",
                hidden=True,
            )
        )
        self.session.add(InventorySession())
        self.session.commit()


db = Despinassy()

if __name__ == "__main__":
    app = db.init_app(config={})
    db.create_all(app=app)
