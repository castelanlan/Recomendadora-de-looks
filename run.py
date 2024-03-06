from App import app

import logging
from log import CustomFormatter

logger = logging.Logger("main")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
