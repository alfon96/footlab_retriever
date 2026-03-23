from logging import LogRecord, Filter, DEBUG
from typing import override
import json


class NoMongoDBDebugLogs(Filter):
    def __init__(self, name=""):
        super().__init__(name)

    @override
    def filter(self, record) -> bool | LogRecord:
        if (
            record.pathname
            and record.levelno <= DEBUG
            and record.pathname.find("pymongo")
        ):
            return False
        return record
