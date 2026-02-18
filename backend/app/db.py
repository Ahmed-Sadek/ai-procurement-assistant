from pymongo import MongoClient
from app.config import settings


def get_database():
    client = MongoClient(settings.MONGO_URI)
    return client[settings.MONGO_DB_NAME]


class MongoWrapper:
    """Generic MongoDB wrapper for query and aggregation operations."""

    def __init__(self, collection_name: str = "purchase_orders"):
        db = get_database()
        self.collection = db[collection_name]

    def run_query(
        self,
        query_dict: dict,
        projection: dict | None = None,
        limit: int = 0,
    ) -> list[dict]:
        cursor = self.collection.find(query_dict, projection)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)

    def run_aggregation(self, pipeline: list[dict]) -> list[dict]:
        return list(self.collection.aggregate(pipeline))
