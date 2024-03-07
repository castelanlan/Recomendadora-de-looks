from App import app, CustomFormatter

import os
import logging

if __name__ == "__main__":
    
    with open('secrets.txt', 'r') as f:
        key = f.read()
    
    os.environ["OPENAI_API_KEY"] = key
    
    logger = logging.Logger("Main")
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)

    logger.info("Run")
    app.run(port=5000, debug=True)
