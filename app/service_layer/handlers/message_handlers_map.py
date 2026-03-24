from app.domain.events import (
    footlab_events,
    scraper_events,
    game_events,
    journal_events,
    persist_events,
)
from app.service_layer.handlers import (
    persist_handlers,
    footlab_handlers,
    journal_handlers,
    message_handlers_map,
    normalization_handlers,
    scraper_handlers,
)
from app.domain import commands


def get_command_handers(logger):
    return {
        commands.ReadJournal: lambda cmd, events: journal_handlers.read_journal(
            cmd=cmd, collected_events=events, logger=logger
        )
    }


def get_scraper_handlers(repository, logger):
    return {
        scraper_events.ScrapeRequestReceived: [
            lambda evt, events: persist_handlers.check_data_on_db(
                evt=evt, repo=repository, collected_events=events, logger=logger
            )
        ],
        scraper_events.AlreadyScraped: [
            lambda evt, events: footlab_handlers.route_footlab_item(
                evt=evt, collected_events=events, logger=logger
            )
        ],
    }


def get_journal_handlers(base_api, logger):
    return {
        journal_events.JournalRetrieved: [
            lambda evt, events: journal_handlers.process_journal(
                evt=evt, collected_events=events, base_api_url=base_api, logger=logger
            )
        ],
    }


def get_persist_handlers(repository, logger, scraper):
    return {
        persist_events.DbItemNotFound: [
            lambda evt, events: scraper_handlers.scrape_url(
                evt=evt, scraper=scraper, collected_events=events, logger=logger
            )
        ],
        persist_events.DbItemReadOk: [
            lambda evt, events: footlab_handlers.route_footlab_item(
                evt=evt, collected_events=events, logger=logger
            )
        ],
        persist_events.DbInsertionRequested: [
            lambda evt, events: persist_handlers.save_data_on_scraped_db(
                evt=evt, repo=repository, collected_events=events, logger=logger
            )
        ],
        persist_events.DbItemCreated: [
            lambda evt, events: footlab_handlers.route_footlab_item(
                evt=evt, collected_events=events, logger=logger
            )
        ],
        persist_events.DbItemUpdated: [
            lambda evt, events: footlab_handlers.route_footlab_item(
                evt=evt, collected_events=events, logger=logger
            )
        ],
    }


def get_game_handlers(repository, logger, scraper, base_api: str):
    return {
        game_events.GameRawDataStored: [
            lambda evt, events: normalization_handlers.transform_games(
                evt=evt,
                collected_events=events,
                logger=logger,
            )
        ],
        game_events.GameCreated: [
            lambda evt, events: footlab_handlers.find_additional_game_data(
                evt=evt,
                collected_events=events,
                base_api=base_api,
                logger=logger,
            )
        ],
        # game_events.LineupsRawDataStored: [
        #     lambda evt, events: normalization_handlers.transform_lineups(
        #         evt=evt,
        #         collected_events=events,
        #         logger=logger,
        #     )
        # ],
        # game_events.LineupsCreated: [
        #     lambda evt, events: scraper_handlers.find_additional_game_data(
        #         evt=evt,
        #         collected_events=events,
        #         base_api=base_api,
        #         logger=logger,
        #     )
        # ],
    }
