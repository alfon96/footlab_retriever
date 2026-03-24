from pydantic import BaseModel


class Command(BaseModel):
    pass


class ReadJournal(Command):
    path: str
