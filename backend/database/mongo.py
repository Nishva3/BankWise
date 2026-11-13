from pymongo import MongoClient, ASCENDING, DESCENDING


class Database:
    def __init__(self, uri):
        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.db = self.client.get_default_database()

    def init_indexes(self):
        for name in ("users", "bank_statements", "transactions", "classification_rules", "model_feedback", "anomaly_records", "anomaly_dismissals", "processing_logs", "model_versions"):
            self.db[name]
        self.db.users.create_index("email", unique=True)
        self.db.bank_statements.create_index([("owner_id", ASCENDING), ("created_at", DESCENDING)])
        self.db.transactions.create_index([("owner_id", ASCENDING), ("date", DESCENDING)])
        self.db.transactions.create_index([("owner_id", ASCENDING), ("final_category", ASCENDING), ("date", DESCENDING)])
        self.db.transactions.create_index([("owner_id", ASCENDING), ("fingerprint", ASCENDING)], unique=True,
                                          partialFilterExpression={"fingerprint": {"$type": "string"}})
        self.db.transactions.create_index([("statement_id", ASCENDING)])
        self.db.classification_rules.create_index([("enabled", ASCENDING), ("priority", DESCENDING)])
        self.db.model_feedback.create_index([("owner_id", ASCENDING), ("transaction_id", ASCENDING)], unique=True)
        self.db.anomaly_records.create_index([("owner_id", ASCENDING), ("created_at", DESCENDING)])
        self.db.anomaly_dismissals.create_index([("owner_id", ASCENDING), ("transaction_id", ASCENDING), ("reason", ASCENDING)], unique=True)
        self.db.processing_logs.create_index([("owner_id", ASCENDING), ("statement_id", ASCENDING), ("created_at", DESCENDING)])
        self.db.model_versions.create_index([("version_number", DESCENDING)], unique=True, sparse=True)
        self.db.model_versions.create_index([("created_at", DESCENDING)])

