from app.domain.events import Event
from dataclasses import asdict
import redis
import json
import logging

r = redis.Redis()
logger = logging.getLogger(__name__)


def publish(channel: str, event: Event):
    logging.info("publishing: channel=%s, event=%s", channel, event)
    r.publish(channel=channel, message=json.dumps(asdict(event)))
