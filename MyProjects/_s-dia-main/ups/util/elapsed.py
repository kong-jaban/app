from datetime import datetime
from ups.util.log import get_logger

logger = get_logger()

DATE_FORMAT_STRING = '%Y-%m-%d %H:%M:%S'
CNT = 60


class Elapsed:
    def __init__(self, name=None, depth=0, dash=False) -> None:
        self.name = name
        self.depth = depth
        self.dash = dash
        self.start_time = datetime.now()
        self.start(self.name)

    def _dash(self):
        return ('=' if self.depth == 0 else '-') * 60

    def start(self, msg='') -> None:
        if self.dash:
            logger.info(f'{"\t" * self.depth}{self._dash()}')
        logger.info(f'{"\t" * self.depth}[start] {msg}')
        if self.dash:
            logger.info(f'{"\t" * self.depth}{self._dash()}')

    def end(self, msg='') -> None:
        current = datetime.now()
        if self.dash:
            logger.info(f'{"\t" * self.depth}{self._dash()}')
        logger.info(f'{"\t" * self.depth}[finished] {self.name}: {current - self.start_time}: {msg}')
        if self.dash:
            logger.info(f'{"\t" * self.depth}{self._dash()}')

    def current(self, msg='') -> None:
        current = datetime.now()
        logger.info(f'{"\t" * self.depth}[elapsed] {self.name}:{current - self.start_time}: {msg}')
