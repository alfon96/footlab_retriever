from app.adapters.repository import repository
from app.adapters.repository.sc_repo import BaseScDbItem
from app.domain.events import persist_events
from app.adapters.repository import repository
from logging import Logger


def save_data_on_scraped_db(
    evt: persist_events.DbInsertionRequested,
    repo: repository.AbstractRepository,
    collected_events: list,
    logger: Logger = None,
):
    """Persist the scraped ScrapeTask instance"""

    try:
        upsert_enum: repository.UpsertResult = repo.upsert(input_data=evt.item)
    except Exception as e:
        collected_events.append(
            persist_events.DbItemSavedKo(item=evt.item, details=str(e))
        )
        raise e
    else:
        match upsert_enum:
            case repository.UpsertResult.INSERTED:
                collected_events.append(
                    persist_events.DbItemCreated(**evt.model_dump())
                )
            case repository.UpsertResult.UPDATED:
                collected_events.append(
                    persist_events.DbItemUpdated(**evt.model_dump())
                )
            case repository.UpsertResult.UNCHANGED:
                collected_events.append(
                    persist_events.DbItemUnchanged(**evt.model_dump())
                )


def check_data_on_db(
    evt: persist_events.DbReadRequested,
    repo: repository.AbstractRepository,
    collected_events: list,
    logger: Logger = None,
):
    try:
        db_item = repo.read(query=evt)

        if db_item:
            collected_events.append(persist_events.DbItemReadOk(item=evt))
        else:
            collected_events.append(persist_events.DbItemNotFound(item=evt))
    except Exception as e:
        print(e)
        try:
            collected_events.append(persist_events.DbItemNotFound(item=evt))
        except Exception as e:
            raise e
