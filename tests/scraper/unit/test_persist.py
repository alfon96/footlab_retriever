import pytest
from app.domain.model import FullDbItem, ScraperTask
from app.domain.events import (
    ScrapeSucceeded,
    PersistFailed,
    DbItemCreated,
)
from app.service_layer.handlers import save_data_on_db


class FakeSuccessfulScraperRepo:
    def upsert(self, input_data: FullDbItem) -> str:
        return "007"

    def read(self, url: str) -> FullDbItem | None:
        return FullDbItem(url=url, data={"some-key": 42}, expires_at=100, season=26)

    def delete(self, url: str) -> bool:
        return True


class FakeBrokenScraperRepo:
    def upsert(self, input_data: FullDbItem) -> str:
        raise Exception("Don't work on a friday")

    def read(self, url: str) -> FullDbItem | None:
        raise Exception("Don't work on a friday")

    def delete(self, url: str) -> bool:
        raise Exception("Don't work on a friday")


def test_save_data_on_db_success():
    scrape_succeeded_event = ScrapeSucceeded(
        content=ScraperTask(url="fake-endpoint", data={"some-key": 42}, season=26)
    )

    events = []
    save_data_on_db(
        evt=scrape_succeeded_event,
        repository=FakeSuccessfulScraperRepo(),
        events=events,
    )

    [event] = events
    assert isinstance(event, DbItemCreated)


def test_save_data_on_db_failure():
    with pytest.raises(Exception):
        scrape_succeeded_event = ScrapeSucceeded(
            content=ScraperTask(url="fake-endpoint", data={"some-key": 42}, season=26)
        )

        events = []
        save_data_on_db(
            evt=scrape_succeeded_event,
            repository=FakeBrokenScraperRepo(),
            events=events,
        )

        [event] = events
        assert isinstance(event, PersistFailed)
