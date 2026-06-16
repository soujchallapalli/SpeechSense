import os

import pymongo
from pymongo.collection import Collection
from pymongo.server_api import ServerApi


class BaseMongoRepository:
    def __init__(
        self,
        collection_name: str,
    ) -> None:
        """Initializes the connection and binds this specific instance to a collection."""
        uri = os.getenv("MONGODB_URI")
        self.client: pymongo.MongoClient = pymongo.MongoClient(uri, server_api=ServerApi("1"))
        self.db = self.client["SpeechSenseDB"]
        self.collection: Collection = self.db[collection_name]

    def get_by_id(self, row_num: int) -> dict | None:
        """Returns a single document based on its _id."""
        return self.collection.find_one({"_id": row_num})

    def get_all(self) -> list:
        """Returns all documents in the collection as a list."""
        return list(self.collection.find({}))

    def insert(self, row_id: int, row: dict) -> int:
        """Inserts a new document into the collection."""
        row["_id"] = row_id
        result = self.collection.insert_one(row)
        return int(result.inserted_id)

    def update(self, row_num: int, updated_row: dict) -> int:
        """Updates a document in the collection based on its _id."""
        result = self.collection.update_one({"_id": row_num}, {"$set": updated_row})
        return result.modified_count

    def delete(self, row_num: int) -> int:
        """Deletes a document from the collection based on its _id."""
        result = self.collection.delete_one({"_id": row_num})
        return result.deleted_count

    def empty_collection(self) -> None:
        """Deletes all documents in the collection."""
        self.collection.delete_many({})
