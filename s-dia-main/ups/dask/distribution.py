import io
from pathlib import Path
import shutil
import dask.dataframe as dd
import re
from typing import Callable, Dict, Tuple, Union, List, Literal

import pandas as pd
from ups.dask.column_util import get_iqr_bounds, get_sigma_bounds
from ups.dask.valid_check import str_to_list, valid_check_column_exists
from ups.util.progress_callback import ProgressCallback, TaskTrackingCallback


def get_distribution(
    df: dd.DataFrame,
    out_dir: str,
    columns: Union[str, List[str]] = None,
    sort_by_count: bool = True,
    ascending: bool = True,
    callback: Callable = None,
) -> dd.DataFrame:
    """
    분포 뽑는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    out_dir : str
        결과 저장 디렉토리
        컬럼별 분포 파일: <디렉토리>/<컬럼명>.csv (header=True, encoding='utf-8', sep=',')
    columns : str or list
        분포 뽑을 컬럼 이름 또는 컬럼 목록
    sort_by_count : bool, default=True
        결과를 카운트 기준으로 정렬할지 여부
    ascending : bool, default=False
        정렬 순서 (False: 내림차순, True: 오름차순)
    callback : Callable, default=None
        progress 콜백 함수
    """
    columns = str_to_list(columns)
    valid_check_column_exists(df, columns)

    def _func(col, sf):
        dx = sf.value_counts()
        dx = dx.reset_index().rename(columns={0: 'count'})
        sort_by = 'count' if sort_by_count else col
        dx = dx.sort_values(sort_by, ascending=ascending, na_position='first')
        dx.to_csv(
            f'{out_dir}/{col}.csv',
            single_file=True,
            header=True,
            encoding='euc-kr',
            sep=',',
            index=False,
        )

    if callback:
        with ProgressCallback(callback=callback, loop_count=len(columns), loop_compute_count=1):
            for col in columns:
                _func(col, df[col])
    else:
        for col in columns:
            _func(col, df[col])
    return


def get_number_outlier(
    df: dd.DataFrame,
    path: str,
    columns: Union[str, List[str]] = None,
    include_1_99_percentile: bool = False,
    include_15iqr: bool = False,
    include_3sigma: bool = False,
    exclude_values: List[Union[int, float]] = None,
    callback: Callable = None,
) -> dd.DataFrame:
    """
    분포 뽑는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    path : str
        결과 저장 파일 경로
    columns : str or list
        분포 뽑을 컬럼 이름 또는 컬럼 목록
    include_1_99_percentile : bool, default=False
        1% ~ 99% 분위수 포함 여부
    include_15iqr : bool, default=False
        15iqr 포함 여부
    include_3sigma : bool, default=False
        3sigma 포함 여부
    exclude_values : str or list, default=None
        제외할 값 목록
    callback : Callable, default=None
        progress 콜백 함수
    """
    columns = str_to_list(columns)
    valid_check_column_exists(df, columns)

    def _get_agg_list(sf):
        aggs = {
            '유의미값개수': sf.count(),
            'min': sf.min(),
            'max': sf.max(),
            '01%': sf.quantile(0.01),
            '25%': sf.quantile(0.25),
            '50%': sf.quantile(0.5),
            '75%': sf.quantile(0.75),
            '99%': sf.quantile(0.99),
        }
        if not include_1_99_percentile:
            del aggs['01%']
            del aggs['99%']
        return aggs

    def _func(col, sf):
        agg = {}
        agg['컬럼'] = col
        agg['전체개수'] = sf.count().compute()
        sf = sf[~sf.isna()]
        agg['null제외개수'] = sf.count().compute()
        if exclude_values:
            sf = sf[~sf.isin(exclude_values)]
        agg_list = _get_agg_list(sf)
        vs = dd.compute(*agg_list.values())
        for k, v in zip(agg_list.keys(), vs):
            agg[k] = v
        if include_15iqr:
            bounds_iqr = get_iqr_bounds(sf, real_data=True, exclude_values=exclude_values)
            agg['1.5iqr_left'] = bounds_iqr[0]
            agg['1.5iqr_right'] = bounds_iqr[1]
        if include_3sigma:
            bounds_sigma = get_sigma_bounds(sf, real_data=True, exclude_values=exclude_values)
            agg['3sigma_left'] = bounds_sigma[0]
            agg['3sigma_right'] = bounds_sigma[1]
        return agg

    outliers = []

    if callback:
        with ProgressCallback(callback=callback, loop_count=len(columns), loop_compute_count=7):
            for col in columns:
                outliers.append(_func(col, df[col]))
    else:
        for col in columns:
            outliers.append(_func(col, df[col]))

    pd.DataFrame(outliers).to_csv(
        path,
        header=True,
        encoding='euc-kr',
        sep=',',
        index=False,
    )
    return
