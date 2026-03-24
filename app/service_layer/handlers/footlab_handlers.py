from app.adapters.scraper import AbstractScraper
from app.domain.models import footlab_models
from app.domain.events import game_events, persist_events, scraper_events
from app.adapters.repository import sc_repo
from pydantic import ValidationError
from logging import Logger


def route_footlab_item(
    evt: persist_events.DbItemCreated,
    collected_events: list,
    logger: Logger = None,
):
    try:
        assert isinstance(evt.item, sc_repo.CompleteScraperDbItem)
        match evt.item.category:
            case footlab_models.FootlabCategory.GAMES:
                collected_events.append(game_events.GameRawDataStored(evt.item))
            case footlab_models.FootlabCategory.LINEUPS:
                collected_events.append(game_events.LineupsRawDataStored(evt.item))
            case footlab_models.FootlabCategory.HEATMAPS:
                collected_events.append(game_events.HeatmapsRawDataStored(evt.item))
            case footlab_models.FootlabCategory.STATISTICS:
                collected_events.append(game_events.StatisticsRawDataStored(evt.item))
            case footlab_models.FootlabCategory.STANDINGS:
                collected_events.append(game_events.StandingsRawDataStored(evt.item))
            case footlab_models.FootlabCategory.CALENDAR:
                collected_events.append(game_events.CalendarRawDataStored(evt.item))
            case footlab_models.FootlabCategory.TEAMS:
                collected_events.append(game_events.TeamsRawDataStored(evt.item))
            case footlab_models.FootlabCategory.PLAYERS:
                collected_events.append(game_events.PlayersRawDataStored(evt.item))
    except ValidationError as e:
        logger.exception(e.json())
        raise e


def find_additional_game_data(
    evt: game_events.GameCreated,
    collected_events: list,
    base_api: str,
    logger: Logger = None,
):
    game_tasks = {
        "incidents": footlab_models.FootlabCategory.INCIDENTS,
        "managers": footlab_models.FootlabCategory.MANAGER,
        "graph": footlab_models.FootlabCategory.GRAPH,
        "votes": footlab_models.FootlabCategory.VOTES,
        "lineups": footlab_models.FootlabCategory.LINEUPS,
        "average-positions": footlab_models.FootlabCategory.AVERAGE_POSITIONS,
        "statistics": footlab_models.FootlabCategory.STATISTICS,
        "best-players/summary": footlab_models.FootlabCategory.BEST_PLAYERS_SUMMARY,
    }
    team_tasks = {"heatmap": footlab_models.FootlabCategory.HEATMAPS}
    # player_tasks = {"rating-breakdown": ScraperCategory.RATING_BREAKDOWN}
    try:
        for key, cat in game_tasks.items():
            collected_events.append(
                scraper_events.ScrapeRequestReceived(
                    url=f"{base_api}/event/{evt.item.game_id}/{key}",
                    season=evt.item.season,
                    category=cat,
                )
            )

        team_ids = [evt.item.home_team["id"], evt.item.away_team["id"]]

        for team_id in team_ids:
            for key, cat in team_tasks.items():
                collected_events.append(
                    scraper_events.ScrapeRequestReceived(
                        url=f"{base_api}/event/{evt.item.game_id}/{key}/{team_id}",
                        season=evt.item.season,
                        category=cat,
                    )
                )
        return
    except Exception as e:
        print(f"Error generating scrape requests for game {evt.item.game_id}: {e}")
