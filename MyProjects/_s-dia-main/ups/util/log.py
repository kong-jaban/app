import logging
from pathlib import Path
from typing import Union


# ###########################################
# get_current_time = lambda : datetime.now().strftime("%Y%m%d%H%M%S")


###########################################
def get_logger(
    logName: str = 's-dia',
    logLevel: Union[int, str] = logging.INFO,
    logFile: str = './s-dia.log',
) -> logging.Logger:
    if isinstance(logLevel, str):
        logLevel = logLevel.upper()

    streamHandler = logging.StreamHandler()
    fileHandler = logging.FileHandler(Path(logFile).expanduser().resolve(), encoding='utf-8')

    logging.basicConfig(
        level=logLevel,
        datefmt='%Y-%m-%d %H:%M:%S',
        # format='%(asctime)s:%(name)s:%(levelname)s:%(message)s',
        # format='%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(lineno)d:%(message)s',
        format='%(asctime)s:%(levelname)s:%(message)s',
        handlers=[streamHandler, fileHandler],
    )
    logger = logging.getLogger(logName)
    return logger
