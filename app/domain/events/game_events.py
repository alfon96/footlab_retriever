from app.domain.models import game_models
from app.domain.events.base_events import Event
from app.adapters.repository import sc_repo
from pydantic import ConfigDict, BaseModel


class GameBase(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, arbitrary_types_allowed=True, extra="ignore"
    )


class GameRawDataStored(Event, GameBase):

    item: sc_repo.CompleteScraperDbItem


class GameCreated(Event):
    item: game_models.FootlabGame


class LineupsRawDataStored(Event, GameBase):
    item: sc_repo.CompleteScraperDbItem


class LineupsCreated(Event):
    item: game_models.FootlabLineup


class HeatmapsRawDataStored(Event, GameBase):
    item: sc_repo.CompleteScraperDbItem


class StatisticsRawDataStored(Event, GameBase):
    item: sc_repo.CompleteScraperDbItem


class StandingsRawDataStored(Event, GameBase):
    item: sc_repo.CompleteScraperDbItem


class CalendarRawDataStored(Event, GameBase):
    item: sc_repo.CompleteScraperDbItem


class TeamsRawDataStored(Event, GameBase):
    item: sc_repo.CompleteScraperDbItem


class PlayersRawDataStored(Event, GameBase):
    item: sc_repo.CompleteScraperDbItem
