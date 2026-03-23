from app.scraper.service_layer.messagebus import MessageBus
from app.scraper.adapters.repository import AbstractRepository, MongoDbRepository
from app.scraper.adapters.scraper import AbstractScraper, PlaywrightScraper


BASE_API = "https://www.sofascore.com/api/v1"


def bootstrap(
    repository: AbstractRepository = MongoDbRepository(
        connection_str="mongodb://mongo"
    ),
    scraper: AbstractScraper = PlaywrightScraper(),
) -> MessageBus:

    return MessageBus(repository=repository, scraper=scraper, base_api=BASE_API)
