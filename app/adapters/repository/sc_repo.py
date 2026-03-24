from app.adapters.repository import repository
from pymongo import ASCENDING, IndexModel
from app.domain.models import footlab_models
from pydantic import BaseModel


class BaseScDbItem(BaseModel):
    url: str
    season: int
    category: footlab_models.FootlabCategory


class CompleteScraperDbItem(BaseScDbItem):
    data: dict
    expires_at: float = 0.0


class MongoSraperRepository(
    repository.MongoDbRepository["BaseScDbItem", "CompleteScraperDbItem"]
):
    def __init__(self, connection_str: str, logger=None):
        super().__init__(
            connection_str=connection_str,
            complete_model=CompleteScraperDbItem,
            logger=logger,
        )

    def get_filter(self, item) -> dict:
        return {"url": item.url}

    def _ensure_indexes(self) -> None:
        index = IndexModel([("url", ASCENDING)], unique=True)
        for db_name in self.client.list_database_names():
            if not db_name.startswith("Season"):
                continue
            db = self.client[db_name]
            for collection in db.list_collection_names():
                db[collection].create_indexes([index])

    def _get_collection(self, item):
        db_name = f"Season_{item.season}"
        db = self.client.get_database(db_name)

        return db[item.category.value]
