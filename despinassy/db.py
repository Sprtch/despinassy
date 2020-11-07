from sqlalchemy import orm
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model
from functools import update_wrapper

def setupmethod(f):
    def wrapper_func(self, *args, **kwargs):
        return f(self, *args, **kwargs)
    return update_wrapper(wrapper_func, f)

class NO_APP:
    extensions = {
        'sqlalchemy': None,
    }
    config = {
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///../huron/database.db'
    }
    root_path=''

    def __init__(self):
        self.teardown_appcontext_funcs = []
        self.debug = False

    @setupmethod
    def teardown_appcontext(self, f):
        self.teardown_appcontext_funcs.append(f)
        return f

class Despinassy(SQLAlchemy):
    def __init__(self):
        super().__init__(
            query_class=orm.Query,
            model_class=Model,
        )

    def init_app(self, app=None):
        if app is None:
            app = NO_APP()
            self.app = app
            super().init_app(app)
        else:
            super().init_app(app)

db = Despinassy()
