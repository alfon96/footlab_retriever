import abc
from typing import Protocol
from app.scraper.domain.model import FullDbItem, BaseDbItem
from pymongo import MongoClient
from app.logs.config.setup_logs import logger
from pymongo.results import UpdateResult, DeleteResult
from enum import Enum
from pymongo import ASCENDING, IndexModel


class UpsertEnum(Enum):
    INSERTED = 0
    UPDATED = 1
    UNCHANGED = 2


class AbstractRepository(Protocol):
    def upsert(self, input_data: FullDbItem) -> UpsertEnum:
        pass

    def read(self, collection: str, url: str) -> FullDbItem | None:
        pass

    def delete(self, collection: str, url: str) -> bool:
        pass


class MongoDbRepository:
    """The mongodb DB will consist of several databases
    named SeasonXX each one containing collections like
    GAMES, PLAYERS, etc. where we store the meaningful
    data as documents."""

    def __init__(self, connection_str: str):
        self.client = MongoClient(connection_str)
        self._ensure_index_for_all_dbs()

    def get_db_collection(self, season: int, collection: str):
        db_name = f"Season_{season}"
        db = self.client.get_database(db_name)

        return db[collection]

    def upsert(self, input_data: FullDbItem) -> UpsertEnum:
        try:
            collection = self.get_db_collection(
                season=input_data.season, collection=input_data.category
            )

            result: UpdateResult = collection.update_one(
                filter={"url": input_data.url},
                update={"$set": input_data.model_dump()},
                upsert=True,
            )
        except Exception as e:
            logger.exception(e)
            raise e
        else:
            if result.upserted_id is not None:
                return UpsertEnum.INSERTED

            if result.modified_count > 0:
                return UpsertEnum.UPDATED

            return UpsertEnum.UNCHANGED

    def read(self, db_item: BaseDbItem) -> FullDbItem | None:
        try:
            collection = self.get_db_collection(
                season=db_item.season, collection=db_item.category
            )
            document: dict = collection.find_one(filter={"url": db_item.url})
        except Exception as e:
            raise e
        else:
            if document:
                del document["_id"]
                try:
                    return FullDbItem(**document)
                except:
                    raise
        return

    def delete(self, db_item: BaseDbItem):
        try:
            collection = self.get_db_collection(
                season=db_item.season, collection=db_item.category
            )
            result: DeleteResult = collection.delete_one(filter={"url": db_item.url})
        except Exception as e:
            raise e
        else:
            if result.deleted_count > 0:
                return True
        return False

    def _ensure_index_for_all_dbs(self):
        url_index = IndexModel([("url", ASCENDING)], unique=True)
        all_dbs = self.client.list_database_names()
        season_dbs = [name for name in all_dbs if name.startswith("Season")]

        for db_name in season_dbs:
            db = self.client.get_database(db_name)
            collections = db.list_collection_names()
            for collection in collections:
                db[collection].create_indexes([url_index])
