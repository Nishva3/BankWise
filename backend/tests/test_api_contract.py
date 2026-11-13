from bson import ObjectId
from flask_jwt_extended import create_access_token
import app as backend_app


class Collection:
    def __init__(self): self.last_query = None
    def find_one(self, query, *args, **kwargs): self.last_query = query; return None


class FakeDB:
    def __init__(self):
        self.transactions = Collection(); self.users = Collection()


class FakeDatabase:
    def __init__(self, uri): self.db = FakeDB(); self.client = self
    def init_indexes(self): pass


class TestConfig(backend_app.Config):
    SECRET_KEY = "test-signing-secret-with-at-least-32-bytes"
    JWT_SECRET_KEY = SECRET_KEY
    MODEL_DIR = "test-models"


def test_unauthorized_transaction_request_is_rejected(monkeypatch):
    monkeypatch.setattr(backend_app, "Database", FakeDatabase)
    app = backend_app.create_app(TestConfig)
    response = app.test_client().get("/api/transactions")
    assert response.status_code == 401


def test_transaction_fetch_is_owner_scoped(monkeypatch):
    monkeypatch.setattr(backend_app, "Database", FakeDatabase)
    app = backend_app.create_app(TestConfig)
    user_id = ObjectId()
    with app.app_context(): token = create_access_token(identity=str(user_id))
    response = app.test_client().get("/api/transactions/" + str(ObjectId()), headers={"Authorization": "Bearer " + token})
    assert response.status_code == 404
    assert app.extensions["bankwise_db"].transactions.last_query == {"_id": ObjectId(response.request.path.split("/")[-1]), "owner_id": user_id}
