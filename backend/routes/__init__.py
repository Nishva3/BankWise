from .auth import bp as auth_bp
from .statements import bp as statements_bp
from .transactions import bp as transactions_bp
from .classification import bp as classification_bp
from .analytics import bp as analytics_bp
from .anomalies import bp as anomalies_bp
from .export import bp as export_bp
from .data_management import bp as data_management_bp


def register_blueprints(app):
    for blueprint in (auth_bp, statements_bp, transactions_bp, classification_bp, analytics_bp, anomalies_bp, export_bp, data_management_bp):
        app.register_blueprint(blueprint)
