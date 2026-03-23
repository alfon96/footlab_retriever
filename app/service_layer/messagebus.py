from app.scraper.domain.events import Event
from app.scraper.domain.commands import Command
from typing import Union
from app.scraper.domain import events
from app.scraper.adapters.scraper import AbstractScraper
from app.scraper.adapters.repository import AbstractRepository
from app.scraper.service_layer import handlers
from tenacity import Retrying, RetryError, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)

Message = Union[Event, Command]


class MessageBus:
    def __init__(
        self,
        repository: AbstractRepository,
        scraper: AbstractScraper,
        base_api: str,
        publisher: callable = lambda: "",
    ):
        self.scraper = scraper
        self.repository = repository
        self.publisher = publisher
        self.base_api = base_api
        self._wire()

    def handle(self, message: Message):
        self.queue = [message]
        while self.queue:
            message = self.queue.pop(0)
            if isinstance(message, Event):
                self.handle_events(event=message)
            elif isinstance(message, Command):
                self.handle_commands(command=message)
            else:
                raise ValueError("Not recognized type of Message")
        pass

    def handle_events(self, event: Event):
        for handler in self.event_handlers.get(type(event)):
            try:
                for attempt in Retrying(
                    stop=stop_after_attempt(3), wait=wait_exponential()
                ):
                    with attempt:
                        collected_events = []
                        logger.info(
                            f"Processing {type(event).__name__}, retry: {attempt.retry_state.attempt_number}"
                        )
                        handler(event, collected_events)
                        self.queue.extend(collected_events)
            except RetryError as retry_failure:
                logger.error(
                    "Failed to handle event %s times, giving up!",
                    retry_failure.last_attempt.attempt_number,
                )
                continue

    def handle_commands(self, command: Command):
        handler = self.command_handlers.get(type(command))
        if handler:
            collected_events = []
            handler(command, collected_events)
            self.queue.extend(collected_events)

    def _wire(self):
        self.command_handlers = {}
        self.event_handlers = {
            events.ScrapeRequestReceived: [
                lambda evt, events: handlers.check_data_on_db(
                    evt=evt, repository=self.repository, events=events
                )
            ],
            events.DbItemNotFound: [
                lambda evt, events: handlers.scrape_url(
                    evt=evt, scraper=self.scraper, events=events
                )
            ],
            events.ScrapeSucceeded: [
                lambda evt, events: handlers.save_data_on_db(
                    evt=evt, repository=self.repository, events=events
                )
            ],
            events.AlreadyScraped: [
                lambda evt, events: handlers.route_scrape_results(
                    evt=evt, events=events
                )
            ],
            events.DbItemCreated: [
                lambda evt, events: handlers.route_scrape_results(
                    evt=evt, events=events
                )
            ],
            events.DbItemUpdated: [
                lambda evt, events: handlers.route_scrape_results(
                    evt=evt, events=events
                )
            ],
            events.GamesReceived: [
                lambda evt, events: handlers.transform_games(evt=evt, events=events)
            ],
            events.GameObjCreated: [
                lambda evt, events: handlers.find_additional_game_data(
                    evt=evt, events=events, base_api=self.base_api
                )
            ],
        }
