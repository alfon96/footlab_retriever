from app.adapters.scraper import AbstractScraper
from app.adapters.repository import fl_repo
from app.domain.events import game_events
from app.domain.models import footlab_models, game_models
from pydantic import ValidationError
from logging import Logger


def get_game_id_from_url(url: str):
    return ""


def transform_games(
    evt: game_events.GameRawDataStored,
    collected_events: list,
    logger: Logger = None,
):
    """Raw Scraper Data to be turned into Games Object"""
    games: list = evt.item.data.get("events", [])
    for game in games:
        assert game and isinstance(game, dict)
        try:
            game["season"] = evt.item.season
            game["game_id"] = get_game_id_from_url(evt.item.url)
            game_created: fl_repo.CompleteFlDbItem = game_models.FootlabGame(**game)

            if game_created:
                collected_events.append(game_events.GameCreated(game_created))
        except ValidationError as e:
            print(e.json())
            continue
    return


# def transform_lineups(
#     evt: game_events.LineupsReceived, collected_events: list, logger: Logger = None
# ):
#     try:
#         lineups_obj = game_models.FootlabLineup(
#             **evt.data, season=evt.season, game_id=evt.game
#         )
#     except ValidationError as e:
#         print(e.json())

#     collected_events.append(game_events.LineupsObjCreated(**lineups_obj.model_dump()))
#     return
