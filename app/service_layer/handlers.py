from app.scraper.adapters.repository import AbstractRepository, UpsertEnum
from app.scraper.adapters.scraper import AbstractScraper
from app.scraper.domain.model import (
    BaseDbItem,
    FullDbItem,
    ScraperCategory,
    ScrapedGame,
)
from app.scraper.domain.events import (
    GameObjCreated,
    ScrapeRequestReceived,
    ScrapeSucceeded,
    ScrapeFailed,
    AlreadyScraped,
    DbItemNotFound,
    DbItemCreated,
    DbItemUnchanged,
    DbItemUpdated,
    PersistFailed,
    CompleteDbItemEvent,
    GamesReceived,
    LineupsReceived,
    HeatmapsReceived,
    StatisticsReceived,
    StandingsReceived,
    CalendarReceived,
    TeamsReceived,
    PlayersReceived,
)
from pydantic import ValidationError
import logging


logger = logging.getLogger(__name__)


class ScraperError(Exception):
    pass


class NoResultsFromScraper(Exception):
    pass


def publish_db_item_created_event(
    event: DbItemCreated,
    publish: callable,
):
    publish("line_allocated", event)


def publish_db_item_updated_event(
    event: DbItemUpdated,
    publish: callable,
):
    publish("line_allocated", event)


def scrape_url(
    evt: DbItemNotFound,
    scraper: AbstractScraper,
    events: list,
) -> None:
    """Scrapes the url and returns a ScrapeTask instance"""
    try:
        result: dict = scraper.run(url=evt.url)
        if not result:
            raise NoResultsFromScraper("The scraper didn't retrieve any info.")
        scraped_data: dict = _analyze_body(result)

    except Exception as e:
        events.append(
            ScrapeFailed(
                url=evt.url,
                season=evt.season,
                details=str(e),
                category=evt.category,
            )
        )
        raise e
    else:
        events.append(
            ScrapeSucceeded(
                season=evt.season,
                url=evt.url,
                data=scraped_data,
                category=evt.category,
            )
        )


def check_data_on_db(
    evt: ScrapeRequestReceived,
    repository: AbstractRepository,
    events: list,
):
    try:
        params = {"url": evt.url, "season": evt.season, "category": evt.category}
        db_item: FullDbItem = repository.read(BaseDbItem(**params))

        if db_item:
            events.append(AlreadyScraped(**params, data=db_item.data))
        else:
            events.append(DbItemNotFound(**params))
    except Exception:
        events.append(
            DbItemNotFound(url=evt.url, season=evt.season, category=evt.category)
        )


def route_scrape_results(evt: CompleteDbItemEvent, events: list):
    try:

        match evt.category:
            case ScraperCategory.GAMES:
                events.append(GamesReceived(**evt.model_dump()))
            case ScraperCategory.LINEUPS:
                events.append(LineupsReceived(**evt.model_dump()))
            case ScraperCategory.HEATMAPS:
                events.append(HeatmapsReceived(**evt.model_dump()))
            case ScraperCategory.STATISTICS:
                events.append(StatisticsReceived(**evt.model_dump()))
            case ScraperCategory.STANDINGS:
                events.append(StandingsReceived(**evt.model_dump()))
            case ScraperCategory.CALENDAR:
                events.append(CalendarReceived(**evt.model_dump()))
            case ScraperCategory.TEAMS:
                events.append(TeamsReceived(**evt.model_dump()))
            case ScraperCategory.PLAYERS:
                events.append(PlayersReceived(**evt.model_dump()))
    except ValidationError as e:
        logger.exception(e.json())
        raise e


def transform_games(evt: GamesReceived, events: list):
    games = evt.data.get("events", [])
    for game in games:
        assert game and isinstance(game, dict)
        try:
            game["season"] = evt.season
            scraped_game = ScrapedGame(**game)
            if scraped_game:
                events.append(GameObjCreated(**scraped_game.model_dump()))
        except ValidationError as e:
            # logger.info(e.json())
            print(e.json())
            continue
    return


def find_additional_game_data(evt: GameObjCreated, events: list, base_api: str):
    game_tasks = {
        "incidents": ScraperCategory.INCIDENTS,
        "managers": ScraperCategory.MANAGER,
        "graph": ScraperCategory.GRAPH,
        "votes": ScraperCategory.VOTES,
        "lineups": ScraperCategory.LINEUPS,
        "average-positions": ScraperCategory.AVERAGE_POSITIONS,
        "statistics": ScraperCategory.STATISTICS,
        "best-players/summary": ScraperCategory.BEST_PLAYERS_SUMMARY,
    }
    team_tasks = {"heatmap": ScraperCategory.HEATMAPS}
    # player_tasks = {"rating-breakdown": ScraperCategory.RATING_BREAKDOWN}
    try:
        for key, cat in game_tasks.items():
            events.append(
                ScrapeRequestReceived(
                    url=f"{base_api}/event/{evt.game_id}/{key}",
                    season=evt.season,
                    category=cat,
                )
            )

        team_ids = [evt.home_team["id"], evt.away_team["id"]]

        for team_id in team_ids:
            for key, cat in team_tasks.items():
                events.append(
                    ScrapeRequestReceived(
                        url=f"{base_api}/event/{evt.game_id}/{key}/{team_id}",
                        season=evt.season,
                        category=cat,
                    )
                )
        return
    except Exception as e:
        print(f"Error generating scrape requests for game {evt.game_id}: {e}")


def save_data_on_db(
    evt: ScrapeSucceeded,
    repository: AbstractRepository,
    events: list,
):
    """Persist the scraped ScrapeTask instance"""

    try:
        db_item = FullDbItem(
            url=evt.url,
            season=evt.season,
            category=evt.category,
            data=evt.data,
            expires_at=0.0,
        )

        upsert_enum: UpsertEnum = repository.upsert(input_data=db_item)
    except Exception as e:
        events.append(PersistFailed(url=evt.url, details=str(e)))
        raise e
    else:
        match upsert_enum:
            case UpsertEnum.INSERTED:
                events.append(DbItemCreated(**db_item.model_dump()))
            case UpsertEnum.UPDATED:
                events.append(DbItemUpdated(**db_item.model_dump()))
            case UpsertEnum.UNCHANGED:
                events.append(DbItemUnchanged(**db_item.model_dump()))


# ---- Helper Functions ----


def _analyze_body(body: dict):
    """We are calling an API in a browser page to not be detected.
    We need to manually check the status code if there."""

    if not body or len(body.items()) == 0:
        raise NoResultsFromScraper("The scraper didn't retrieve any info.")
    elif "error" in body.keys():
        error_info: dict = body["error"]
        error_code: int = error_info.get("code", 0)
        error_msg: str = error_info.get("message", "No error message found.")

        raise ScraperError(f"Status code: {error_code}, scaped_error_info: {error_msg}")
    return body


def safe_get(input_dictionary: dict, key: str):
    return input_dictionary.get(key, None)
