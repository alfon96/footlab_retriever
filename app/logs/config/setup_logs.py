import logging, json
from pathlib import Path
import logging.config


LOG_CONFIG_PATH = Path("app/logs/config/log_configs.json")
logger = logging.getLogger("my_app")


def _init_logger():

    json_config = {}
    with open(LOG_CONFIG_PATH) as f:
        json_config = json.load(f)

    if json_config:
        logging.config.dictConfig(json_config)
        queue_handler = logging.getHandlerByName("queue_handler")
        if queue_handler is not None:
            import atexit

            queue_handler.listener.start()
            atexit.register(queue_handler.listener.stop)

    else:
        raise Exception("Log config file is empty.")


_init_logger()
