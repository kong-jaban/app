import argparse
import gc
from pathlib import Path
from typing import Callable
import dask
from ups.util import log, util
from ups.dask import call_function
from ups.run.params import call_params
import dask.dataframe as dd

logger = log.get_logger('flow', 'INFO', 'flow.log')


###########################################
class Flow:
    def __init__(self, ymls: list[str]):
        self.cfg = util.load_ymls(ymls, encoding='utf-8')
        self.logger = log.get_logger(
            self.cfg['log']['name'], self.cfg['log']['level'], self.cfg['log']['file']
        )
        self.callback = None

    def set_callback(self, callback: Callable):
        self.callback = callback

    def run(self) -> None:
        dask.config.set(scheduler='threads')

        df = None
        df = self.run_function(df, self.cfg['flow']['start'])
        gc.collect()

        if self.cfg['flow'].get('process', None):
            for fn in self.cfg['flow']['process']:
                df = self.run_function(df, fn)
                gc.collect()

        if self.cfg['flow'].get('end', None):
            self.run_function(df, self.cfg['flow']['end'])

    def run_function(self, df: dd.DataFrame, fn: dict):
        self.logger.info(f'run: {fn["function"]} 실행')
        self.logger.info(f'run: {fn["parameters"]}')

        # datasource 쓰는 함수를 위해 추가
        fn['parameters'] = self.add_env_to_datasource(fn['parameters'])

        if fn['function'] in ['read_parquet', 'write_parquet', 'read_csv', 'write_csv']:
            params = call_params(fn['function'], fn['parameters'])
        else:
            params = fn['parameters']

        self.logger.info(f'run: {fn["function"]}: {params}')
        if fn['function'] in ['write_parquet', 'write_csv', 'get_distribution', 'get_number_outlier']:
            df = call_function(fn['function'], df, callback=self.callback, **params)
        else:
            df = call_function(fn['function'], df, **params)

        return df

    def add_env_to_datasource(self, params: dict):
        if 'datasource' in params:
            params['datasource']['env'] = self.cfg['env']
            return params

        for k, v in params.items():
            if isinstance(v, dict) and 'datasource' in v:
                v['datasource']['env'] = self.cfg['env']
                return params

        return params


###########################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--yml', required=True, action='append', help='설정 파일 경로')
    args = parser.parse_args()

    for ii, x in enumerate(args.yml):
        args.yml[ii] = Path(x).expanduser().resolve()

    def _callback(x):
        logger.info(
            f'{x['current_schedule']} / {x['total_schedules']} schedules, '
            f'({x['current_schedule_completed_tasks']} / {x['current_schedule_tasks']}) tasks/schedule'
        )

    flow = Flow(args.yml)
    flow.set_callback(_callback)
    # flow.set_callback(lambda x, y: print(f'progress: {x}\n{y}'))
    flow.run()
