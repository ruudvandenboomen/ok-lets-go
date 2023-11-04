from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy as _BaseSQLAlchemy


class SQLAlchemy(_BaseSQLAlchemy):
    def apply_pool_defaults(self, app, options):
        options = super().apply_pool_defaults(app, options)
        options["pool_pre_ping"] = True
        return options


db = SQLAlchemy()
migrate = Migrate()
