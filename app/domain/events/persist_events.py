from typing import TypeVar, Generic
from pydantic import BaseModel
from app.domain.events.base_events import Event

T_Base = TypeVar("T_Base", bound=BaseModel)
T_Complete = TypeVar("T_Complete", bound=BaseModel)


class DbInsertionRequested(Event, Generic[T_Complete]):
    item: T_Complete


class DbReadRequested(Event, Generic[T_Base]):
    item: T_Base


# Upsert results


class DbItemCreated(Event, Generic[T_Complete]):
    item: T_Complete


class DbItemUpdated(Event, Generic[T_Complete]):
    item: T_Complete


class DbItemUnchanged(Event, Generic[T_Complete]):
    item: T_Complete


# --


class DbItemReadOk(Event, Generic[T_Complete]):
    item: T_Complete


class DbItemNotFound(Event, Generic[T_Base]):
    item: T_Base


class DbItemDeletedOk(Event):
    pass


class DbItemSavedKo(Event, Generic[T_Complete]):
    item: T_Complete
    details: str


class DbItemDeletedKo(Event, Generic[T_Base]):
    item: T_Base
