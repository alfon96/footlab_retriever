from app.adapters.repository import repository
from pymongo import ASCENDING, IndexModel
from app.domain.models import footlab_models
from pydantic import BaseModel


class BaseFlDbItem(BaseModel):
    game_id: int
    season: int
    category: footlab_models.FootlabCategory


class CompleteFlDbItem(BaseFlDbItem):
    data: dict
    expires_at: float = 0.0


class MongoFootlabRepository(
    repository.MongoDbRepository["BaseFlDbItem", "CompleteFlDbItem"]
):

    def __init__(self, connection_str: str, logger=None):
        super().__init__(
            connection_str=connection_str,
            complete_model=CompleteFlDbItem,
            logger=logger,
        )

    def get_filter(self, item) -> dict:
        return {"game_id": item.game_id}

    def _ensure_indexes(self) -> None:
        index = IndexModel([("game_id", ASCENDING)], unique=True)
        for db_name in self.client.list_database_names():
            if not db_name.startswith("Footlab"):
                continue
            db = self.client[db_name]
            for collection in db.list_collection_names():
                db[collection].create_indexes([index])

    def _get_collection(self, item):
        db_name = f"Footlab_{item.season}"
        db = self.client.get_database(db_name)

        return db[item.category.value]
