from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, UTC
from enum import StrEnum
from pydantic import BaseModel, Field, ConfigDict
from typing import Any

DEFAULT_ETA_IN_DAYS = timedelta(days=365)


class ScraperCategory(StrEnum):
    GAMES = "games"
    INCIDENTS = "incidents"
    MANAGER = "manager"
    GRAPH = "graph"
    VOTES = "votes"
    LINEUPS = "lineups"
    HEATMAPS = "heatmaps"
    AVERAGE_POSITIONS = "average_positions"
    BEST_PLAYERS_SUMMARY = "best_players_summary"
    RATING_BREAKDOWN = "rating_breakdown"
    STATISTICS = "statistics"
    STANDINGS = "standings"
    CALENDAR = "calendar"
    TEAMS = "teams"
    PLAYERS = "players"


class BaseDbItem(BaseModel):
    season: int
    url: str
    category: ScraperCategory


class ScraperTask(BaseDbItem):
    pass


class FullDbItem(BaseDbItem):
    data: dict
    expires_at: float = (datetime.now(UTC) + DEFAULT_ETA_IN_DAYS).timestamp()


class TournamentNameEnum(StrEnum):
    SERIE_A = "SerieA"
    COPPA_ITALIA = "CoppaItalia"
    CHAMPIONS_LEAGUE = "ChampionsLeague"


class TournamentTypeEnum(StrEnum):
    NATIONAL_LEAGUE = "national_league"
    NATIONAL_CUP = "national_cup"
    INTERNATIONAL_CUP = "international_cup"


class Tournament(BaseModel):
    name: str
    season_id: int
    id: int
    start_round: int
    end_round: int
    type: TournamentTypeEnum
    next_available_utc_timestamp: float
    season_human: int


class Journal(BaseModel):
    tournaments: list[Tournament]
    rounds: dict[TournamentNameEnum, list[str]]


# Domain models for Footlab


class ScrapedGame(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    game_id: int = Field(alias="id")
    start_timestamp: float = Field(alias="startTimestamp")
    slug: str

    has_player_statistics: bool = Field(alias="hasEventPlayerStatistics")
    has_heatmaps: bool = Field(alias="hasEventPlayerHeatMap")
    final_result_only: bool = Field(alias="finalResultOnly")

    status: dict[str, Any]
    home_team: dict[str, Any] = Field(alias="homeTeam")
    away_team: dict[str, Any] = Field(alias="awayTeam")
    home_score: dict[str, Any] = Field(alias="homeScore")
    away_score: dict[str, Any] = Field(alias="awayScore")
    round_info: dict[str, Any] = Field(alias="roundInfo")
    season: int = 0
