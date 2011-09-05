
import logging
import logging.handlers

LOG_FILENAME = "log.txt"
log = None

class MemHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)

        self.lst_records = []
        self.status = {
                0:"NotSet",
                10:"Debug",
                20:"Info",
                30:"Warning",
                40:"Error",
                50:"Critical"
                }

    def emit(self, record):
        self.lst_records.append(record)

    def get_logs(self):
        text = ""
        for record in self.lst_records:
            status = self.status.get(record.levelno, "Unknown")
            msg = self.formatter.format(record)
            text += status + ": " + msg + "\n"
        self.lst_records = []
        return text 

def setup_logger(level="info", name="renmas", format="%(message)s"):
    
    LEVELS = {
            'debug':logging.DEBUG,
            'info':logging.INFO,
            'warning':logging.WARNING,
            'error':logging.ERROR,
            'critical':logging.CRITICAL
            }

    logger = logging.getLogger(name)
    logger.setLevel(LEVELS[level])

    #different formatters
    formatter = logging.Formatter(format)

    m = MemHandler()
    m.setFormatter(formatter)
    logger.addHandler(m)

    global log
    log = logger
    return logger

setup_logger()

