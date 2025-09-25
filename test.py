import logging
from datetime import datetime as dt
from logging.handlers import TimedRotatingFileHandler

date = dt.now().strftime("%m-%d-%Y, Hour %H Min %M Sec %S")

logging.basicConfig(
    level=logging.DEBUG, # Set a global logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.StreamHandler(), # Log to console
        TimedRotatingFileHandler(f'tools\\fourpp\\logs\\{date}.log', when = "D", backupCount= 5)
    ]
)

logging.info("Test log entry from test.py")