import logging

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    blue = "\x1b[34;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    pink = "\x1b[0;35m"
    reset = "\x1b[0m"
    # format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    title = pink + '%(name)-5s :: ' + reset
    format =  '%(levelname)-8s :: %(message)s'
    FORMATS = {
        logging.DEBUG: title + grey + format + reset,
        logging.INFO: title + blue + format + reset,
        logging.WARNING: title + yellow + format + reset,
        logging.ERROR: title + red + format + reset,
        logging.CRITICAL: title + bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
