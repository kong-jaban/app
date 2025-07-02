from datetime import datetime
import re
from typing import List, Literal, Union
from dask import dataframe as dd
from dateutil.relativedelta import relativedelta
import pandas as pd

from ups.dask.valid_check import (
    raise_error_datetime,
    str_to_list,
    valid_check_column_count,
    valid_check_column_exists,
    valid_check_column_integer,
    valid_check_date_unit,
)


def date_diff(
    df: dd.DataFrame,
    output_column: str = None,
    left: str = None,
    right: str = None,
    unit: Literal['years', 'months', 'days', 'hours', 'minutes', 'seconds'] = 'days',
    errors: Literal['raise', 'coerce'] = 'coerce',
) -> dd.DataFrame:
    """
    두 날짜 컬럼의 차이를 계산하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    output_column : str
        결과를 저장할 새 컬럼 이름
    start_column : str
        시작 날짜 컬럼 이름 또는 datetime(year, month, day, hour, minute, second)
    end_column : str
        종료 날짜 컬럼 이름 또는 datetime(year, month, day, hour, minute, second)
    unit : str, default='days'
        결과 단위
        - 'years': 연도
        - 'months': 월
        - 'days': 일수
        - 'hours': 시간
        - 'minutes': 분
        - 'seconds': 초
    errors : str, default='coerce'
        - 'raise': 오류 발생
        - 'coerce': null 값으로 변환

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame

    Examples:
    --------
    # 일수 차이 계산
    df = date_diff(df, 'start_date', 'end_date')

    # 시간 차이 계산
    df = date_diff(df, 'login_time', 'logout_time',
                  unit='hours',
                  output_column='session_hours')

    # 월수 차이 계산
    df = date_diff(df, 'join_date', 'resign_date',
                  unit='months',
                  output_column='tenure_months')
    """

    def _get_column_or_datetime(c):
        if c in df.columns:
            if df[c].dtype.kind != 'M':
                # raise: error, coerce: null, ignore: 원래값
                df[c] = dd.to_datetime(df[c], errors=errors)
            return df[c]

        if c.startswith('datetime'):
            return datetime(*[int(x) for x in re.split(r'[,()]', c)[1:-1]])

        raise_error_datetime(c)

    # right = _get_column_or_datetime(right)
    # left = _get_column_or_datetime(left)

    unit = valid_check_date_unit(unit)

    # 차이 계산
    diffs = _get_column_or_datetime(left) - _get_column_or_datetime(right)

    # 단위별 변환
    if unit == "years":
        df[output_column] = diffs.dt.year - diffs.dt.year
    elif unit == "months":
        df[output_column] = (diffs.dt.year - diffs.dt.year) * 12 + (diffs.dt.month - diffs.dt.month)
    elif unit == "days":
        df[output_column] = diffs.dt.days
    elif unit == "hours":
        df[output_column] = diffs.dt.days * 24 + diffs.dt.total_seconds() // 3600  # 60*60
    elif unit == "minutes":
        df[output_column] = diffs.dt.days * 1440 + diffs.dt.total_seconds() // 60  # 24*60
    elif unit == "seconds":
        df[output_column] = diffs.dt.days * 86400 + diffs.dt.total_seconds()  # 24*60*60

    return df


def date_add(
    df: dd.DataFrame,
    columns: Union[str, List[str]] = None,
    years: Union[int, str] = 0,
    months: Union[int, str] = 0,
    days: Union[int, str] = 0,
    hours: Union[int, str] = 0,
    minutes: Union[int, str] = 0,
    seconds: Union[int, str] = 0,
    output_columns: Union[str, List[str]] = None,
    errors: Literal['raise', 'coerce'] = 'coerce',
) -> dd.DataFrame:
    """
    날짜 컬럼에 연/월/일/시/분/초를 각각 지정하여 더하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : str or list
        처리할 날짜 컬럼 이름 또는 이름들의 리스트
    years : int or str, default=0
        더할 연도
        - int: 모든 행에 동일한 값
        - str: 값이 있는 컬럼 이름
    months : int or str, default=0
        더할 월
        - int: 모든 행에 동일한 값
        - str: 값이 있는 컬럼 이름
    days : int or str, default=0
        더할 일
        - int: 모든 행에 동일한 값
        - str: 값이 있는 컬럼 이름
    hours : int or str, default=0
        더할 시간
        - int: 모든 행에 동일한 값
        - str: 값이 있는 컬럼 이름
    minutes : int or str, default=0
        더할 분
        - int: 모든 행에 동일한 값
        - str: 값이 있는 컬럼 이름
    seconds : int or str, default=0
        더할 초
        - int: 모든 행에 동일한 값
        - str: 값이 있는 컬럼 이름
    output_columns : str or list, default=None
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
        None일 경우 원본 컬럼을 덮어씀
    errors : str, default='coerce'
        - 'raise': 오류 발생
        - 'coerce': null 값으로 변환

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame
    """
    columns = str_to_list(columns)
    valid_check_column_exists(df, columns)
    output_columns = columns if output_columns is None else str_to_list(output_columns)
    valid_check_column_count(columns, output_columns)

    # 컬럼명으로 지정된 경우 해당 컬럼 존재 여부 확인
    for name, value in [
        ("years", years),
        ("months", months),
        ("days", days),
        ("hours", hours),
        ("minutes", minutes),
        ("seconds", seconds),
    ]:
        if isinstance(value, str):
            valid_check_column_exists(df, [value])
            valid_check_column_integer(df, value)

    # 각 컬럼에 대해 처리 수행
    for col in columns:
        # 날짜형으로 변환
        if df[col].dtype.kind != 'M':
            df[col] = dd.to_datetime(df[col], errors=errors)

    def _apply(dx, out_cols, cols, deltas):
        get_value = lambda row, x: row[x] if isinstance(x, str) else x

        def add_delta(row, col):
            return row[col] + relativedelta(
                years=get_value(row, deltas.get('years', 0)),
                months=get_value(row, deltas.get('months', 0)),
                days=get_value(row, deltas.get('days', 0)),
                hours=get_value(row, deltas.get('hours', 0)),
                minutes=get_value(row, deltas.get('minutes', 0)),
                seconds=get_value(row, deltas.get('seconds', 0)),
            )

        for col, out_col in zip(cols, out_cols):
            dx[out_col] = dx.apply(lambda row: add_delta(row, col), axis=1)

        return dx

    # 메타데이터 생성
    meta = df._meta.copy()
    for col in output_columns:
        meta[col] = pd.Series([], dtype='datetime64[ns]')

    df = df.map_partitions(
        lambda df: _apply(
            df,
            output_columns,
            columns,
            {
                'years': years,
                'months': months,
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds,
            },
        ),
        meta=meta,
    )

    return df
