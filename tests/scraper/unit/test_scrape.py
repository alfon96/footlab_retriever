import pytest
from app.service_layer.handlers import (
    scrape_url,
    NoResultsFromScraper,
    ScraperError,
)
from app.domain.model import ScraperTask
from app.domain.events import ScrapeSucceeded, ScrapeFailed


class FakeSuccessfulScraper:
    def run(self, url: str) -> dict:
        return {
            "url": url,
            "data": {"some_key": 42},
        }


class FakeEmptyScraper:
    def run(self, url: str) -> None:
        return None


class FakeNotFoundScraper:
    def run(self, url: str) -> None:
        return {"error": {"code": 404, "message": "Not Found"}}


def test_scrape_url_success():
    url = "fake-endpoint"
    season = 26
    events = []
    scrape_url(
        evt=ScraperTask(url=url, season=season),
        scraper=FakeSuccessfulScraper(),
        events=events,
        repository=None,
    )

    [event] = events
    assert isinstance(event, ScrapeSucceeded)

    assert event.url == url
    assert event.season == season
    assert event.data
    assert event.data


def test_scrape_url_retrieved_no_info():
    with pytest.raises(
        NoResultsFromScraper, match="The scraper didn't retrieve any info."
    ):
        events = []
        scrape_url(
            evt=ScraperTask(url="fake-endpoint", season=26),
            scraper=FakeEmptyScraper(),
            events=events,
        )
        [event] = events
        assert isinstance(event, ScrapeFailed)


def test_scrape_url_has_bad_status_code():
    with pytest.raises(ScraperError, match="Status code: 404"):
        events = []
        scrape_url(
            evt=ScraperTask(url="fake-endpoint", season=26),
            scraper=FakeNotFoundScraper(),
            events=[],
        )
        [event] = events
        assert isinstance(event, ScrapeFailed)
