from app.domain.models import journal_models
from app.domain.events.base_events import Event


class JournalRetrieved(Event):
    journal: journal_models.Journal


class JournalUpdated(Event):
    pass
