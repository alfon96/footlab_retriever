from logging import Formatter, LogRecord
from typing import override
import json


class JSONFormatter(Formatter):
    def __init__(self, *, fmt_keys: dict[str, str] | None = None):
        super().__init__()
        self._fmt = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: LogRecord) -> str:
        return json.dumps(record.__dict__, default=str)
