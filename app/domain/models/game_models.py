from pydantic import BaseModel, Field, ConfigDict
from typing import Any


class FootlabGameBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    game_id: int = Field(alias="id")
    season: int = 0


class FootlabGame(FootlabGameBase):
    status: dict[str, Any]
    start_timestamp: float = Field(alias="startTimestamp")
    slug: str

    has_player_statistics: bool = Field(alias="hasEventPlayerStatistics")
    has_heatmaps: bool = Field(alias="hasEventPlayerHeatMap")
    final_result_only: bool = Field(alias="finalResultOnly")

    home_team: dict[str, Any] = Field(alias="homeTeam")
    away_team: dict[str, Any] = Field(alias="awayTeam")
    home_score: dict[str, Any] = Field(alias="homeScore")
    away_score: dict[str, Any] = Field(alias="awayScore")
    round_info: dict[str, Any] = Field(alias="roundInfo")


class FootlabLineup(FootlabGameBase):
    confirmed: bool
    home: dict[str, Any]
    away: dict[str, Any]


class FootlabHeatmap(FootlabGameBase):
    confirmed: bool
    home: dict[str, Any]
    away: dict[str, Any]


class FootlabIncident(FootlabGameBase):
    confirmed: bool
    home: dict[str, Any]
    away: dict[str, Any]


class FootlabGameStatistics(FootlabGameBase):
    confirmed: bool
    home: dict[str, Any]
    away: dict[str, Any]


class FootlabGameManager(FootlabGameBase):
    confirmed: bool
    home: dict[str, Any]
    away: dict[str, Any]


class FootlabGameVotes(FootlabGameBase):
    confirmed: bool
    home: dict[str, Any]
    away: dict[str, Any]


class FootlabGameAvePos(FootlabGameBase):
    confirmed: bool
    home: dict[str, Any]
    away: dict[str, Any]


class FootlabGameBestPlayers(FootlabGameBase):
    confirmed: bool
    home: dict[str, Any]
    away: dict[str, Any]
