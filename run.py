from App import app

import logging
from log import CustomFormatter

loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
for logger in loggers:
    logger.setLevel(logging.INFO)

logger = logging.Logger("main")
ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
