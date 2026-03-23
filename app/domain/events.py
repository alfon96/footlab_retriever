from pydantic import BaseModel
from dataclasses import dataclass
from app.scraper.domain.model import ScrapedGame, ScraperCategory


class Event(BaseModel):
    pass


class BaseEvent(Event):
    season: int
    url: str
    category: ScraperCategory


class CompleteDbItemEvent(BaseEvent):
    data: dict
    expires_at: float = 0.0


# Scraper Events


class ScrapeRequestReceived(BaseEvent):
    pass


class AlreadyScraped(BaseEvent):
    data: dict


class ScrapeFailed(BaseEvent):
    details: str


class ScrapeSucceeded(BaseEvent):
    data: dict


# DB Events
class GamesObjCreated(Event):
    pass


class PersistFailed(BaseEvent):
    pass


class DbItemCreated(CompleteDbItemEvent):
    pass


class DbItemUpdated(CompleteDbItemEvent):
    pass


class DbItemUnchanged(CompleteDbItemEvent):
    pass


class DbItemNotFound(BaseEvent):
    pass


# Persisted Data Events


class GamesReceived(CompleteDbItemEvent):
    pass


class LineupsReceived(CompleteDbItemEvent):
    pass


class HeatmapsReceived(CompleteDbItemEvent):
    pass


class StatisticsReceived(CompleteDbItemEvent):
    pass


class StandingsReceived(CompleteDbItemEvent):
    pass


class CalendarReceived(CompleteDbItemEvent):
    pass


class TeamsReceived(CompleteDbItemEvent):
    pass


class PlayersReceived(CompleteDbItemEvent):
    pass


class GameObjCreated(Event, ScrapedGame):
    pass
