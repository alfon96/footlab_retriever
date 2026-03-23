from celery import chain
from app.celery.tasks import scrape_and_persist, analyze_scraped, dmap, extract_
from app.core.scraper.start_scrape import get_urls_to_scrape

if __name__ == "__main__":
    urls = get_urls_to_scrape()
    if not urls:
        raise Exception("No urls to scrape")
    for url in urls:
        c = chain(
            scrape_and_persist.s(url=url), analyze_scraped.s(), dmap.s(extract_.s())
        )()

        c.get()
        print("Here")
