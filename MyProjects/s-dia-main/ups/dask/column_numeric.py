from typing import List, Literal, Union
import dask.dataframe as dd
import pandas as pd
from ups.dask.column_util import (
    get_iqr_bounds,
    get_sigma_bounds,
)
import numpy as np
from ups.dask.valid_check import (
    str_to_list,
    valid_check_bound,
    valid_check_bound_value,
    valid_check_column_count,
    valid_check_column_exists,
    valid_check_percentile_range_bottom,
    valid_check_percentile_range_top,
    valid_check_round_decimals,
    valid_check_round_method,
    valid_check_truncate_digits,
    valid_check_min_max,
    valid_check_random_seed,
    valid_check_random_start,
    valid_check_mean,
    valid_check_std,
    valid_check_categorize_unit,
    valid_check_categorize_bins_length,
    valid_check_categorize_bins_order,
    valid_check_categorize_labels_length,
)


def round(
    df: dd.DataFrame,
    columns: Union[str, list] = None,
    decimals: int = 0,
    exclude_values: List[Union[int, float]] = None,
    output_columns: Union[str, list] = None,
) -> dd.DataFrame:
    """
    숫자 컬럼의 값을 반올림, 올림, 내림하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : str or list
        처리할 컬럼 이름 또는 이름들의 리스트
    decimals : int, default=0
        소수점 자릿수
    exclude_values : List[Union[int, float]], default=None
        제외할 값 리스트
    output_columns : str or list, default=None
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
        None일 경우 원본 컬럼을 덮어씀

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame
    """
    columns = str_to_list(columns)
    valid_check_column_exists(df, columns)
    output_columns = columns if output_columns is None else str_to_list(output_columns)
    valid_check_column_count(columns, output_columns)
    valid_check_round_decimals(decimals)
    if exclude_values is None:
        exclude_values = []

    data_type = 'i8' if decimals <= 0 else 'f8'

    def _apply(sf):
        conditions = [sf.isna() | sf.isin(exclude_values)]
        choices = [sf]
        return np.select(conditions, choices, sf.round(decimals))

    # 각 컬럼에 대해 처리 수행
    for col, out_col in zip(columns, output_columns):
        df[out_col] = df[col].map_partitions(_apply, meta=(out_col, data_type))

    return df
    # return rounding(df, columns, decimals, 'round', output_columns)


def round_down(
    df: dd.DataFrame,
    columns: Union[str, list] = None,
    decimals: int = 0,
    exclude_values: List[Union[int, float]] = None,
    output_columns: Union[str, list] = None,
) -> dd.DataFrame:
    return rounding(df, columns, decimals, 'floor', exclude_values, output_columns)


def round_up(
    df: dd.DataFrame,
    columns: Union[str, list] = None,
    decimals: int = 0,
    exclude_values: List[Union[int, float]] = None,
    output_columns: Union[str, list] = None,
) -> dd.DataFrame:
    return rounding(df, columns, decimals, 'ceil', exclude_values, output_columns)


def rounding(
    df: dd.DataFrame,
    columns: Union[str, list] = None,
    decimals: int = 0,
    method: Literal['round', 'floor', 'ceil'] = 'round',
    exclude_values: List[Union[int, float]] = None,
    output_columns: Union[str, list] = None,
) -> dd.DataFrame:
    """
    숫자 컬럼의 값을 반올림, 올림, 내림하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : str or list
        처리할 컬럼 이름 또는 이름들의 리스트
    decimals : int, default=0
        소수점 자릿수
    method : str, default='round'
        처리 방식
        - 'round': 반올림
        - 'floor': 내림
        - 'ceil': 올림
    exclude_values : List[Union[int, float]], default=None
        제외할 값 리스트
    output_columns : str or list, default=None
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
        None일 경우 원본 컬럼을 덮어씀

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame
    """
    columns = str_to_list(columns)
    valid_check_column_exists(df, columns)
    output_columns = columns if output_columns is None else str_to_list(output_columns)
    valid_check_column_count(columns, output_columns)
    valid_check_round_decimals(decimals)
    valid_check_round_method(method)
    if exclude_values is None:
        exclude_values = []

    def _apply(sf):
        fx = np.floor if method == 'floor' else np.ceil
        factor = 10 ** abs(decimals)

        def _func(x):
            if decimals < 0:
                return fx(x / factor) * factor
            else:
                return fx(x * factor) / factor

        conditions = [sf.isna() | sf.isin(exclude_values)]
        choices = [sf]
        return np.select(conditions, choices, _func(sf))

    # 각 컬럼에 대해 처리 수행
    data_type = 'i8' if decimals <= 0 else 'f8'
    for col, out_col in zip(columns, output_columns):
        df[out_col] = df[col].map_partitions(_apply, meta=(out_col, data_type))

    return df


def truncate_to_left(
    df: dd.DataFrame,
    data_type: Literal['int', 'float'] = 'int',
    columns: Union[str, list] = None,
    digits: int = 0,
    exclude_values: List[Union[int, float]] = None,
    output_columns: Union[str, list] = None,
) -> dd.DataFrame:
    """
    숫자의 왼쪽부터 지정한 자리수만 유지하고 나머지는 0으로 바꾸는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    data_type : str, default='int'
        처리 결과 데이터 타입
        - 'int': 정수
        - 'float': 실수
    columns : str or list
        처리할 컬럼 이름 또는 이름들의 리스트
    digits : int
        왼쪽부터 유지할 자리수
    exclude_values : List[Union[int, float]], default=None
        제외할 값 리스트
    output_columns : str or list, default=None
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
        None일 경우 원본 컬럼을 덮어씀

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame
    """

    columns = str_to_list(columns)
    valid_check_column_exists(df, columns)
    output_columns = columns if output_columns is None else str_to_list(output_columns)
    valid_check_column_count(columns, output_columns)
    valid_check_truncate_digits(digits)
    if exclude_values is None:
        exclude_values = []

    def _apply(sf):
        def _func(x):
            sign = np.sign(x)
            x = abs(x)

            # magnitude = np.int(np.floor(np.log10(x)))  # 1 => 0, 10 => 1, 100 => 2, 1000 => 3, ...
            magnitude = np.log10(x).astype(np.int64)  # 1 => 0, 10 => 1, 100 => 2, 1000 => 3, ...
            factor = 10 ** (magnitude - digits + 1)
            truncated = np.trunc(x / factor) * factor
            return sign * truncated

        conditions = [sf.isna() | sf.isin(exclude_values)]
        choices = [sf]
        return np.select(conditions, choices, _func(sf))

    # 각 컬럼에 대해 처리 수행
    data_type = 'f8' if data_type == 'float' else 'i8'
    for col, out_col in zip(columns, output_columns):
        df[out_col] = df[col].map_partitions(_apply, meta=(out_col, data_type))

    return df


def top_bottom_coding(
    df: dd.DataFrame,
    data_type: Literal['int', 'float', 'string'] = 'int',
    columns: Union[str, list] = None,
    bottom: Union[int, float, None] = None,
    bottom_replace: Union[int, float, str, None] = None,
    top: Union[int, float, None] = None,
    top_replace: Union[int, float, str, None] = None,
    exclude_values: List[Union[int, float]] = None,
    output_columns: Union[str, list, None] = None,
) -> dd.DataFrame:
    """
    숫자 컬럼의 상하단 값을 지정된 범위로 제한하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    data_type : str, default='int'
        처리 결과 데이터 타입
        - 'int': 정수
        - 'float': 실수
        - 'string': 문자열
    columns : str or list
        처리할 컬럼 이름 또는 이름들의 리스트
    bottom : int or float, default=None
        하위 경계값
        None일 경우 하위 제한 없음
    bottom_replace : int or float or str, default=None
        하위 경계값 대체값
        None일 경우 하위 경계값으로 대체체
        str일 경우 문자열 형식으로 변환
    top : int or float, default=None
        상위 경계값
        None일 경우 상위 제한 없음
    top_replace : int or float or str, default=None
        상위 경계값 대체값
        None일 경우 상위 경계값으로 대체체
        str일 경우 문자열 형식으로 변환
    exclude_values : List[Union[int, float]], default=None
        제외할 값 리스트
    output_columns : str or list, default=None
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
        None일 경우 원본 컬럼을 덮어씀

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame
    """
    columns = str_to_list(columns)
    valid_check_column_exists(df, columns)
    output_columns = columns if output_columns is None else str_to_list(output_columns)
    valid_check_column_count(columns, output_columns)
    valid_check_bound(top, bottom)
    for x in [bottom, bottom_replace, top, top_replace]:
        valid_check_bound_value(x)
    if exclude_values is None:
        exclude_values = []

    if (bottom is not None) and (bottom_replace is None):
        bottom_replace = bottom
    if (top is not None) and (top_replace is None):
        top_replace = top

    def _apply(sf):
        conditions = [sf.isna() | sf.isin(exclude_values)]
        choices = [sf]
        if bottom is not None:
            conditions.append(sf < bottom)
            choices.append(bottom_replace)

        if top is not None:
            conditions.append(sf > top)
            choices.append(top_replace)

        return np.select(conditions, choices, sf)

    # 각 컬럼에 대해 처리 수행
    for col, out_col in zip(columns, output_columns):
        df[out_col] = df[col].map_partitions(_apply, meta=(out_col, data_type))

    return df


def top_bottom_percentile(
    df: dd.DataFrame,
    columns: Union[str, list] = None,
    bottom: float = None,
    top: float = None,
    exclude_values: List[Union[int, float]] = None,
    output_columns: Union[str, list, None] = None,
) -> dd.DataFrame:
    """
    숫자 컬럼의 상하단 값을 지정된 백분위수 범위로 제한하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : str or list
        처리할 컬럼 이름 또는 이름들의 리스트
    bottom: float, default=None
        하위 백분위수. 0 ~ 50 사이의 값
    top: float, default=None
        상위 백분위수. 50 ~ 100 사이의 값
    exclude_values : List[Union[int, float]], default=None
        제외할 값 리스트
    output_columns : str or list, default=None
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
        None일 경우 원본 컬럼을 덮어씀

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame
    """
    columns = str_to_list(columns)
    valid_check_column_exists(df, columns)
    output_columns = columns if output_columns is None else str_to_list(output_columns)
    valid_check_column_count(columns, output_columns)
    valid_check_bound(top, bottom)
    valid_check_percentile_range_bottom(bottom)  # 0-50
    valid_check_percentile_range_top(top)  # 50-100
    if exclude_values is None:
        exclude_values = []

    def _apply(sf, bottom_bound, top_bound):
        conditions = [sf.isna() | sf.isin(exclude_values)]
        choices = [sf]
        return np.select(conditions, choices, sf.clip(lower=bottom_bound, upper=top_bound))

    # 각 컬럼에 대해 처리 수행
    for col, out_col in zip(columns, output_columns):
        dx = df[~df[col].isna() & ~df[col].isin(exclude_values)]
        sx = dx[col]
        bottom_bound = None if bottom is None else sx[sx >= sx.quantile(bottom / 100)].min().compute()
        top_bound = None if top is None else sx[sx <= sx.quantile(top / 100)].max().compute()

        # print(f'bottom_bound: {bottom_bound}, top_bound: {top_bound}')
        df[out_col] = df[col].map_partitions(_apply, bottom_bound, top_bound, meta=(out_col, df[col].dtype))

    return df


def top_bottom_15iqr(
    df: dd.DataFrame,
    columns: Union[str, list] = None,
    bottom: bool = True,
    top: bool = True,
    exclude_values: List[Union[int, float]] = None,
    output_columns: Union[str, list, None] = None,
) -> dd.DataFrame:
    """
    숫자 컬럼의 상하단 값을 1.5 IQR 범위로 제한하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : str or list
        처리할 컬럼 이름 또는 이름들의 리스트
    bottom : bool, default=False
        하위 1.5 IQR 범위 제한 여부
    top : bool, default=False
        상위 1.5 IQR 범위 제한 여부
    exclude_values : List[Union[int, float]], default=None
        제외할 값 리스트
    output_columns : str or list, default=None
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
        None일 경우 원본 컬럼을 덮어씀

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame
    """
    columns = str_to_list(columns)
    valid_check_column_exists(df, columns)
    output_columns = columns if output_columns is None else str_to_list(output_columns)
    valid_check_column_count(columns, output_columns)
    valid_check_bound(top, bottom)
    if exclude_values is None:
        exclude_values = []

    def _apply(sf, bottom_bound, top_bound):
        conditions = [sf.isna() | sf.isin(exclude_values)]
        choices = [sf]
        return np.select(conditions, choices, sf.clip(lower=bottom_bound, upper=top_bound))

    # 각 컬럼에 대해 처리 수행
    for col, out_col in zip(columns, output_columns):
        bounds = get_iqr_bounds(df[col], multiplier=1.5, real_data=True, exclude_values=exclude_values)
        lower_bound = bounds[0] if bottom else None
        upper_bound = bounds[1] if top else None
        df[out_col] = df[col].map_partitions(_apply, lower_bound, upper_bound, meta=(out_col, df[col].dtype))

    return df


def top_bottom_3sigma(
    df: dd.DataFrame,
    columns: Union[str, list] = None,
    bottom: bool = True,
    top: bool = True,
    exclude_values: List[Union[int, float]] = None,
    output_columns: Union[str, list, None] = None,
) -> dd.DataFrame:
    """
    숫자 컬럼의 상하단 값을 3sigma 범위로 제한하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : str or list
        처리할 컬럼 이름 또는 이름들의 리스트
    bottom : bool, default=False
        하위 3sigma 범위 제한 여부
    top : bool, default=False
        상위 3sigma 범위 제한 여부
    exclude_values : List[Union[int, float]], default=None
        제외할 값 리스트
    output_columns : str or list, default=None
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
        None일 경우 원본 컬럼을 덮어씀

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame
    """
    columns = str_to_list(columns)
    valid_check_column_exists(df, columns)
    output_columns = columns if output_columns is None else str_to_list(output_columns)
    valid_check_column_count(columns, output_columns)
    valid_check_bound(top, bottom)
    if exclude_values is None:
        exclude_values = []

    def _apply(sf, bottom_bound, top_bound):
        conditions = [sf.isna() | sf.isin(exclude_values)]
        choices = [sf]
        return np.select(conditions, choices, sf.clip(lower=bottom_bound, upper=top_bound))

    # 각 컬럼에 대해 처리 수행
    for col, out_col in zip(columns, output_columns):
        bounds = get_sigma_bounds(df[col], multiplier=3, real_data=True, exclude_values=exclude_values)
        lower_bound = bounds[0] if bottom else None
        upper_bound = bounds[1] if top else None
        df[out_col] = df[col].map_partitions(_apply, lower_bound, upper_bound, meta=(out_col, df[col].dtype))

    return df


def categorize_by_unit(
    df: dd.DataFrame,
    columns: Union[str, list] = None,
    unit: Literal[5, 10] = 10,
    method: Literal['floor', 'mean', 'string'] = 'floor',
    exclude_values: List[Union[int, float]] = None,
    output_columns: Union[str, list, None] = None,
) -> dd.DataFrame:
    """
    숫자를 지정된 단위(10 또는 5)로 나누어 범주화하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : str or list
        처리할 컬럼 이름 또는 이름들의 리스트
    unit : int, default=10
        나눌 단위 (10 또는 5)
    method : str, default='floor'
        구간값 방법
        - 'floor': 내림
        - 'mean': 평균
        - 'string': 문자열 형식
    exclude_values : List[Union[int, float]], default=None
        제외할 값 리스트
    output_columns : str or list, default=None
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
        None일 경우 원본 컬럼을 덮어씀

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame

    Examples:
    --------
    # 10단위로 나누기
    df = categorize_by_unit(df, 'age', unit=10)
    # 결과: 23 -> '20-29', 35 -> '30-39'

    # 5단위로 나누기
    df = categorize_by_unit(df, 'score', unit=5)
    # 결과: 82 -> '80-84', 77 -> '75-79'

    # 여러 컬럼 동시 처리
    df = categorize_by_unit(df,
                           columns=['value1', 'value2'],
                           unit=10,
                           output_columns=['value1_group', 'value2_group'])
    """

    columns = str_to_list(columns)
    valid_check_column_exists(df, columns)
    output_columns = columns if output_columns is None else str_to_list(output_columns)
    valid_check_column_count(columns, output_columns)
    valid_check_categorize_unit(unit)
    if exclude_values is None:
        exclude_values = []

    def _apply(sf):
        conditions = [sf.isna() | sf.isin(exclude_values)]
        choices = [sf]

        def _func(x):
            # 하한값 계산
            lower = (x // unit) * unit
            # 상한값 계산
            upper = lower + (unit - 1)

            if method == 'mean':
                return np.ceil((lower + upper) / 2)
            elif method == 'string':
                return f'{lower}-{upper}'
            else:  # method == 'floor'
                return lower

        return np.select(conditions, choices, _func(sf))

    # 각 컬럼에 대해 처리 수행
    for col, out_col in zip(columns, output_columns):
        # 범주화 수행
        df[out_col] = df[col].map_partitions(_apply, meta=(out_col, 'object' if method == 'string' else 'i8'))

    return df


def categorize_by_interval(
    df: dd.DataFrame,
    columns: Union[str, list] = None,
    bins: list = None,
    labels: list = None,
    include_lowest: bool = True,
    right: bool = False,
    extend_bins: bool = True,
    exclude_values: List[Union[int, float]] = None,
    output_columns: Union[str, list, None] = None,
) -> dd.DataFrame:
    """
    숫자 컬럼을 지정된 구간으로 범주화하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : str or list
        처리할 컬럼 이름 또는 이름들의 리스트
    bins : list
        구간 경계값들의 리스트 (오름차순)
    labels : list, default=None
        각 구간에 부여할 레이블 리스트
        None일 경우 자동 생성
        - 구간이 n개일 때 레이블은 n-1개여야 함
    include_lowest : bool, default=True
        True이면 첫 구간에 최솟값을 포함
    right : bool, default=False
        True이면 구간의 오른쪽 경계를 포함 [a, b). 초과-이하
        False이면 구간의 왼쪽 경계를 포함 (a, b]. 이상-미만
    extend_bins : bool, default=True
        True이면 구간 밖의 값을 위해 범위 추가
    output_columns : str or list, default=None
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
        None일 경우 원본 컬럼을 덮어씀

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame

    Examples:
    --------
    # 점수 등급화
    df = categorize_by_interval(df, 'score',
                              bins=[0, 60, 70, 80, 90, 100],
                              labels=['F', 'D', 'C', 'B', 'A'])

    # 소득 구간화
    df = categorize_by_interval(df, 'income',
                              bins=[0, 3000, 5000, 7000, 10000],
                              labels=['저소득', '중하소득', '중간소득', '고소득'])
    """

    columns = str_to_list(columns)
    valid_check_column_exists(df, columns)
    output_columns = columns if output_columns is None else str_to_list(output_columns)
    valid_check_column_count(columns, output_columns)
    valid_check_categorize_bins_length(len(bins))
    valid_check_categorize_bins_order(bins)
    valid_check_categorize_labels_length(labels, len(bins))
    if exclude_values is None:
        exclude_values = []

    if extend_bins:
        bins = [-np.inf] + bins + [np.inf]
        if labels is not None:
            labels = ['-inf'] + labels + ['inf']

    def _apply(sf):
        conditions = [sf.isna() | sf.isin(exclude_values)]
        choices = [sf]
        return np.select(
            conditions,
            choices,
            pd.cut(
                sf, bins=bins, labels=labels, include_lowest=include_lowest, right=right, ordered=True
            ).astype(str),
        )

    # 각 컬럼에 대해 처리 수행
    for col, out_col in zip(columns, output_columns):
        # 범주화 수행
        df[out_col] = df[col].map_partitions(_apply, meta=(out_col, 'object'))

    return df


def categorize_by_equal_width(
    df: dd.DataFrame,
    columns: Union[str, list] = None,
    bins: int = 10,
    labels: list = None,
    exclude_values: List[Union[int, float]] = None,
    output_columns: Union[str, list, None] = None,
) -> dd.DataFrame:
    """
    숫자 컬럼을 균등한 간격으로 범주화하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : str or list
        처리할 컬럼 이름 또는 이름들의 리스트
    bins : int
        균등 간격으로 나눌 구간 수
    labels : list, default=None
        각 구간에 부여할 레이블 리스트
        None일 경우 자동 생성
        - 레이블 개수는 n_bins와 같아야 함
    exclude_values : List[Union[int, float]], default=None
        제외할 값 리스트
    output_columns : str or list, default=None
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
        None일 경우 원본 컬럼을 덮어씀

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame

    Examples:
    --------
    # 5개 구간으로 균등 분할
    df = categorize_by_equal_width(df, 'value', n_bins=5)

    # 레이블 지정하여 4개 구간으로 분할
    df = categorize_by_equal_width(df, 'score',
                                 bins=4,
                                 labels=['낮음', '중하', '중상', '높음'])
    """

    columns = str_to_list(columns)
    valid_check_column_exists(df, columns)
    output_columns = columns if output_columns is None else str_to_list(output_columns)
    valid_check_column_count(columns, output_columns)
    valid_check_categorize_bins_length(bins)
    valid_check_categorize_labels_length(labels, bins)
    if exclude_values is None:
        exclude_values = []

    def _apply(sf):
        conditions = [sf.isna() | sf.isin(exclude_values)]
        choices = [sf]
        return np.select(
            conditions,
            choices,
            pd.cut(sf, bins=bins, labels=labels, include_lowest=True, right=False, ordered=True).astype(str),
        )

    # 각 컬럼에 대해 처리 수행
    for col, out_col in zip(columns, output_columns):
        # 범주화 수행
        df[out_col] = df[col].map_partitions(_apply, meta=(out_col, 'object'))

    return df


def fill_random_int(
    df: dd.DataFrame,
    output_columns: Union[str, list] = None,
    min: int = 0,
    max: int = 100,
    seed: int = None,
) -> dd.DataFrame:
    """
    컬럼을 랜덤 숫자로 채우는 함수
    균등분포 (정수)

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    output_columns : str or list
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
    min : int, default=0
        최솟값
    max : int, default=100
        최댓값
    seed : int, default=None
        랜덤 시드값

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame
    """

    output_columns = str_to_list(output_columns)
    valid_check_min_max(min)
    valid_check_min_max(max)
    valid_check_random_seed(seed)

    # 랜덤 시드 설정
    if seed is not None:
        np.random.seed(seed)

    # 각 컬럼에 대해 처리 수행
    for out_col in output_columns:
        df[out_col] = df.map_partitions(
            lambda x: np.random.randint(low=min, high=max, size=len(x)),  # len(x): 파티션 내 행 수
            meta=(out_col, 'i8'),
        )

    return df


def fill_random_float(
    df: dd.DataFrame,
    output_columns: Union[str, list] = None,
    min: float = 0.0,
    max: float = 1.0,
    seed: int = None,
) -> dd.DataFrame:
    """
    컬럼을 랜덤 숫자로 채우는 함수
    균등분포 (실수)

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    output_columns : str or list
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
    min : float, default=0.0
        최솟값
    max : float, default=1.0
        최댓값
    seed : int, default=None
        랜덤 시드값

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame
    """

    output_columns = str_to_list(output_columns)
    valid_check_min_max(min)
    valid_check_min_max(max)
    valid_check_random_seed(seed)

    # 랜덤 시드 설정
    if seed is not None:
        np.random.seed(seed)

    # 각 컬럼에 대해 처리 수행
    for out_col in output_columns:
        df[out_col] = df.map_partitions(
            lambda x: np.random.uniform(low=min, high=max, size=len(x)),  # len(x): 파티션 내 행 수
            meta=(out_col, 'f8'),
        )

    return df


def fill_random_normal(
    df: dd.DataFrame,
    output_columns: Union[str, list] = None,
    mean: float = 0.0,
    std: float = 1.0,
    seed: int = None,
) -> dd.DataFrame:
    """
    컬럼을 랜덤 숫자로 채우는 함수
    정규분포 (실수)

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    output_columns : str or list
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
    mean : float, default=0.0
        평균값
    std : unsigned float, default=1.0(정규분포)
        표준편차
    seed : int, default=None
        랜덤 시드값

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame
    """
    output_columns = str_to_list(output_columns)
    valid_check_mean(mean)
    valid_check_std(std)
    valid_check_random_seed(seed)

    # 랜덤 시드 설정
    if seed is not None:
        np.random.seed(seed)

    # 각 컬럼에 대해 처리 수행
    for out_col in output_columns:
        df[out_col] = df.map_partitions(
            lambda x: np.random.normal(loc=mean, scale=std, size=len(x)),  # len(x): 파티션 내 행 수
            meta=(out_col, 'f8'),
        )

    return df


def fill_random_sequence(
    df: dd.DataFrame,
    output_columns: Union[str, list] = None,
    start: int = 1,
) -> dd.DataFrame:
    """
    순서가 무작위인 중복되지 않는 일련번호 컬럼을 추가하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    output_column : str
        결과를 저장할 새 컬럼 이름
    start : int, default=1
        시작 번호
    seed : int, default=None
        랜덤 시드값

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame

    Examples:
    --------
    # 기본 사용 (1부터 시작)
    df = add_random_sequence(df, 'sequence_id')

    # 시작 번호 지정
    df = add_random_sequence(df, 'random_id', start=1000)

    # 시드값 지정하여 재현 가능하게
    df = add_random_sequence(df, 'random_seq', seed=42)
    """
    output_columns = str_to_list(output_columns)
    valid_check_random_start(start)

    # DataFrame 크기만큼의 순차적인 배열 생성
    size = df.shape[0].compute()

    for out_col in output_columns:
        seq = np.random.permutation(size) + start
        df_seq = dd.from_pandas(pd.DataFrame({'__seq__': seq}), npartitions=df.npartitions)

        df = df.reset_index(drop=True)
        df_seq = df_seq.reset_index(drop=True)

        df[out_col] = df_seq['__seq__']

    return df
