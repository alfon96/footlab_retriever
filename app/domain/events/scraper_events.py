from app.domain.models import footlab_models
from app.domain.events.base_events import Event


class BaseScraperEvent(Event):
    season: int
    url: str
    category: footlab_models.FootlabCategory


class ScrapeRequestReceived(BaseScraperEvent):
    pass


class AlreadyScraped(BaseScraperEvent):
    data: dict


class ScrapeFailed(BaseScraperEvent):
    details: str


class ScrapeSucceeded(BaseScraperEvent):
    data: dict
