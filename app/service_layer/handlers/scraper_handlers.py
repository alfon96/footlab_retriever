from app.adapters.scraper import AbstractScraper
from app.domain.events import scraper_events
from logging import Logger
from app.domain.models import footlab_models


class ScraperError(Exception):
    pass


class NoResultsFromScraper(Exception):
    pass


def scrape_url(
    evt: scraper_events.ScrapeRequestReceived,
    scraper: AbstractScraper,
    collected_events: list,
    logger: Logger = None,
) -> None:
    """Scrapes the url and returns a ScrapeTask instance"""
    try:
        result: dict = scraper.run(url=evt.url)
        if not result:
            raise NoResultsFromScraper("The scraper didn't retrieve any info.")
        scraped_data: dict = _analyze_body(result)

    except Exception as e:
        collected_events.append(
            scraper_events.ScrapeFailed(**evt.model_dump(), details=str(e))
        )
        raise e
    else:
        collected_events.append(
            scraper_events.ScrapeSucceeded(
                season=evt.season,
                url=evt.url,
                data=scraped_data,
                category=evt.category,
            )
        )


## Utility functions


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
