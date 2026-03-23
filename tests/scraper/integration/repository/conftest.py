from typing import Generator
from app.scraper.adapters.repository import MongoDbRepository
import pytest

TEST_DB_NAME = "repositoryTest"


@pytest.fixture(scope="session")
def mongo_test_instance() -> Generator[MongoDbRepository, None, None]:
    test_mongodb = MongoDbRepository(
        connection_str="mongodb://mongo", db_name=TEST_DB_NAME
    )
    yield test_mongodb
    test_mongodb.client.close()


@pytest.fixture(autouse=True)
def auto_cleanup(mongo_test_instance: MongoDbRepository):
    yield
    mongo_test_instance.client.drop_database(TEST_DB_NAME)
