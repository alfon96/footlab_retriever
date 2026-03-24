from enum import StrEnum
from pydantic import BaseModel


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
