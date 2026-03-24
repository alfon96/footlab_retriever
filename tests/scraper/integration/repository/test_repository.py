from app.adapters.repository.sc_repo import MongoDbRepository
from app.domain.model import ScraperTask, FullDbItem
from pymongo import MongoClient
from tests.scraper.integration.repository.conftest import TEST_DB_NAME


def populate_with_fake_raw_data(
    client: MongoClient, test_db_collection: str = "Season26"
):
    """Returning fake data to insert in the collection Season26"""
    fakes = [
        FullDbItem(
            url="fake-endpoint-1", data={"some-key": 42}, expires_at=100, season=26
        ),
        FullDbItem(
            url="fake-endpoint-2", data={"some-key": 24}, expires_at=500, season=26
        ),
    ]

    client.get_database(TEST_DB_NAME).get_collection(test_db_collection).insert_many(
        documents=[fake.model_dump() for fake in fakes]
    )


def test_insert(mongo_test_instance: MongoDbRepository):
    raw_data = FullDbItem(
        url="fake-endpoint-25", data={"some-key": 42}, expires_at=100, season=26
    )
    # First upsert will write data in the db
    insert_new_data: str = mongo_test_instance.upsert(input_data=raw_data)
    assert insert_new_data

    # Second upsert with the same data will do nothing
    insert_same_data: str = mongo_test_instance.upsert(input_data=raw_data)
    assert insert_same_data is None

    raw_data = FullDbItem(
        url="fake-endpoint-25", data={"some-key": 33}, expires_at=100, season=26
    )

    # Third upsert with different data will update the document
    update_existing_fields: str = mongo_test_instance.upsert(input_data=raw_data)
    assert update_existing_fields is None


def test_read(mongo_test_instance: MongoDbRepository):
    populate_with_fake_raw_data(
        client=mongo_test_instance.client, test_db_collection="Season26"
    )
    url = "fake-endpoint-1"
    raw_data: FullDbItem = mongo_test_instance.read(url=url, category="Season26")
    assert raw_data is not None
    assert isinstance(raw_data, FullDbItem)
    assert raw_data.url == url


def test_delete(mongo_test_instance: MongoDbRepository):
    populate_with_fake_raw_data(
        client=mongo_test_instance.client, test_db_collection="Season26"
    )
    url = "fake-endpoint-1"
    success: bool = mongo_test_instance.delete(url=url, category="Season26")
    assert success
