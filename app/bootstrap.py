from app.service_layer.messagebus import MessageBus
from app.adapters.repository.repository import AbstractRepository
from app.adapters.repository.sc_repo import MongoSraperRepository
from app.adapters.repository.fl_repo import MongoFootlabRepository

from app.adapters.scraper import AbstractScraper, PlaywrightScraper
from logging import Logger
import logging
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

BASE_API = os.environ.get("BASE_API_URL")
MONGO_DB_CONNECTION_STR = os.environ.get("MONGO_DB_CONNECTION_STR")
JOURNAL_PATH = os.environ.get("JOURNAL_PATH")


def bootstrap(
    scraper_repo: AbstractRepository = MongoSraperRepository(
        connection_str=MONGO_DB_CONNECTION_STR,
    ),
    footlab_repo: AbstractRepository = MongoFootlabRepository(
        connection_str=MONGO_DB_CONNECTION_STR,
    ),
    scraper: AbstractScraper = PlaywrightScraper(),
) -> MessageBus:

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    logger: Logger = logging.getLogger(__name__)

    return MessageBus(
        scraper_repo=scraper_repo,
        footlab_repo=footlab_repo,
        scraper=scraper,
        base_api=BASE_API,
        journal_path=JOURNAL_PATH,
        logger=logger,
    )


if __name__ == "__main__":
    pass
