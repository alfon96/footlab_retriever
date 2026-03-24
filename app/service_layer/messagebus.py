from app.domain.events.base_events import Event
from app.domain.commands import Command
from typing import Union
from app.domain import events
from app.domain import commands
from app.adapters.scraper import AbstractScraper
from app.adapters.repository.repository import AbstractRepository
from app.service_layer.handlers import journal_handlers
from app.service_layer.handlers import persist_handlers
from app.service_layer.handlers import scraper_handlers
from app.service_layer.handlers import normalization_handlers
from app.service_layer.handlers import message_handlers_map
from tenacity import Retrying, RetryError, stop_after_attempt, wait_exponential

from logging import Logger
import logging

logger = logging.getLogger(__name__)

Message = Union[Event, Command]


class MessageBus:
    def __init__(
        self,
        scraper_repo: AbstractRepository,
        footlab_repo: AbstractRepository,
        scraper: AbstractScraper,
        journal_path: str,
        base_api: str,
        logger: Logger,
        publisher: callable = lambda: "",
    ):
        self.scraper = scraper
        self.scraper_repo = scraper_repo
        self.footlab_repo = footlab_repo
        self.publisher = publisher
        self.base_api = base_api
        self.journal_path = journal_path
        self.logger = logger
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
                        self.logger.info(
                            f"Processing {type(event).__name__}, retry: {attempt.retry_state.attempt_number}"
                        )
                        handler(event, collected_events)
                        self.queue.extend(collected_events)
            except RetryError as retry_failure:
                self.logger.error(
                    "Failed to handle event %s times, giving up!",
                    retry_failure.last_attempt.attempt_number,
                )
                continue

    def handle_commands(self, command: Command):
        handler = self.command_handlers.get(type(command))
        try:
            for attempt in Retrying(
                stop=stop_after_attempt(3), wait=wait_exponential()
            ):
                with attempt:
                    if handler:
                        collected_events = []
                        self.logger.info(
                            f"Processing {type(command).__name__}, retry: {attempt.retry_state.attempt_number}"
                        )
                        handler(command, collected_events)
                        self.queue.extend(collected_events)
        except RetryError as retry_failure:
            self.logger.error(
                "Failed to handle event %s times, giving up!",
                retry_failure.last_attempt.attempt_number,
            )
            raise

    def _wire(self):
        self.command_handlers = message_handlers_map.get_command_handers(
            logger=self.logger
        )
        self.event_handlers = {
            **message_handlers_map.get_journal_handlers(
                base_api=self.base_api, logger=self.logger
            ),
            **message_handlers_map.get_scraper_handlers(
                repository=self.scraper_repo,
                logger=self.logger,
            ),
            **message_handlers_map.get_persist_handlers(
                logger=self.logger, repository=self.scraper_repo, scraper=self.scraper
            ),
            **message_handlers_map.get_game_handlers(
                logger=self.logger,
                base_api=self.base_api,
                repository=self.scraper_repo,
                scraper=self.scraper,
            ),
        }
