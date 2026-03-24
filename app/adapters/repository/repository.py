from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type, Optional, Protocol, runtime_checkable
from enum import IntEnum
from logging import Logger
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.results import UpdateResult, DeleteResult

T_Base = TypeVar("T_Base", bound=BaseModel)
T_Complete = TypeVar("T_Complete", bound=BaseModel)


class UpsertResult(IntEnum):
    INSERTED = 0
    UPDATED = 1
    UNCHANGED = 2


@runtime_checkable
class AbstractRepository(Protocol):

    def upsert(self, item: T_Complete) -> UpsertResult: ...
    def read(self, query: T_Base) -> T_Complete | None: ...
    def delete(self, query: T_Base) -> bool: ...


class MongoDbRepository(ABC, Generic[T_Base, T_Complete]):
    """
    MongoDb Repository generic implementation. Each sub class shoud define the
    - Base Type
    - Complete type
        to retrieve and insert documents in mongodb. Also it is essential to add
    - get_filter
        which should return the filter dict used to retrieve a document from mongo db.
    - get_collection:
        is used to get the collection object comprehensive of db_name and collection name
    - ensure_indexes
        is a method used to add custom indexes to your collection  and it should
        be overwritten.
    """

    def __init__(
        self,
        connection_str: str,
        complete_model: Type[T_Complete],
        logger: Optional[Logger] = None,
    ) -> None:
        self.client = MongoClient(connection_str)
        self.complete_model = complete_model
        self.logger = logger
        self._ensure_indexes()

    def upsert(self, item: T_Complete) -> UpsertResult:
        result: UpdateResult = self._get_collection(item).update_one(
            filter=self.get_filter(item),
            update={"$set": item.model_dump()},
            upsert=True,
        )
        if result.upserted_id is not None:
            return UpsertResult.INSERTED
        return (
            UpsertResult.UPDATED
            if result.modified_count > 0
            else UpsertResult.UNCHANGED
        )

    def read(self, query: T_Base) -> Optional[T_Complete]:
        doc: dict | None = self._get_collection(query).find_one(self.get_filter(query))
        if doc:
            doc.pop("_id", None)
            return self.complete_model(**doc)
        return None

    def delete(self, query: T_Base) -> bool:
        result: DeleteResult = self._get_collection(query).delete_one(
            self.get_filter(query)
        )
        return result.deleted_count > 0

    @abstractmethod
    def get_filter(self, item: T_Base | T_Complete) -> dict: ...

    @abstractmethod
    def _ensure_indexes(self) -> None: ...

    @abstractmethod
    def _get_collection(self, item: T_Base | T_Complete): ...
