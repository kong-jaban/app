import operator
import re
from typing import Any, Callable, Dict, List, Tuple, Union
from dask import dataframe as dd
from ups.dask.valid_check import valid_check_multiplier, raise_error_value
import yaml

# for eval
# python 내장 함수 아닌 것을 import 해 놔야 쓸 수 있음
# code linter 등에서 지우라고 해도 지우면 안 됨
from datetime import datetime
from math import floor, ceil, sqrt, log, exp, sin, cos, tan, asin, acos, atan, pi, e
from random import random, randint, choice, sample, shuffle

pattern_column_variable = re.compile(r'\$\$\{(.+)\}')


def get_sigma_bounds(
    sf: dd.Series,
    multiplier: float = 3.0,
    exclude_values: List[Union[int, float]] = None,
    real_data: bool = False,
) -> Tuple[float, float]:
    """
    시그마(표준편차) 범위를 얻는 함수

    Parameters:
    -----------
    sf : dask.dataframe.Series
        처리할 Dask Series
    multiplier : float, default=3
        표준편차에 곱할 배수
    exclude_values : List[Union[int, float]], default=None
        제외할 값 리스트
    real_data : bool, default=False
        실제 데이터 사용 여부
        True일 경우 계산값이 아닌 실데이터에 있는 값 반환

    Returns:
    --------
    tuple
        (lower_bound, upper_bound)

    Notes:
    ------
    - 하한 = mean - multiplier * std
    - 상한 = mean + multiplier * std
    """
    valid_check_multiplier(multiplier)
    if exclude_values is None:
        exclude_values = []

    sf = sf[~sf.isna() & ~sf.isin(exclude_values)]

    # 평균과 표준편차 계산
    mean_val = sf.mean()
    std_val = sf.std()
    # if np.isnan(std_val) or std_val == 0:  # 표준편차가 유효하지 않은 경우
    #     return (df[column].min(), df[column].max())

    # 상한/하한 계산
    lower_bound = mean_val - multiplier * std_val
    upper_bound = mean_val + multiplier * std_val
    bounds = dd.compute(lower_bound, upper_bound)

    if real_data:
        bounds = dd.compute(sf[sf >= bounds[0]].min(), sf[sf <= bounds[1]].max())

    return bounds


def get_iqr_bounds(
    sf: dd.Series,
    multiplier: float = 1.5,
    exclude_values: List[Union[int, float]] = None,
    real_data: bool = False,
) -> Tuple[float, float]:
    """
    IQR(사분위수 범위) 얻는 함수

    Parameters:
    -----------
    sf : dask.dataframe.Series
        처리할 Dask Series
    multiplier : float, default=1.5
        IQR에 곱할 배수
    exclude_values : List[Union[int, float]], default=None
        제외할 값 리스트
    real_data : bool, default=False
        실제 데이터 사용 여부
        True일 경우 계산값이 아닌 실데이터에 있는 값 반환

    Returns:
    --------
    tuple
        (lower_bound, upper_bound)

    Notes:
    ------
    - 하한 = Q1 - multiplier * IQR
    - 상한 = Q3 + multiplier * IQR
    - IQR = Q3 - Q1
    """
    valid_check_multiplier(multiplier)
    if exclude_values is None:
        exclude_values = []

    sf = sf[~sf.isna() & ~sf.isin(exclude_values)]

    # Q1, Q3 계산
    q1 = sf.quantile(0.25)
    q3 = sf.quantile(0.75)

    # IQR 계산
    iqr = q3 - q1

    # 상한/하한 계산
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr
    bounds = dd.compute(lower_bound, upper_bound)

    if real_data:
        bounds = dd.compute(sf[sf >= bounds[0]].min(), sf[sf <= bounds[1]].max())

    return bounds


def parse_conditions(
    df: dd.DataFrame,
    conditions: Dict[str, Any],
) -> Callable:
    """
    조건에 따른 컬럼 값 조회

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    conditions : Dict[str, Any]
        조건 딕셔너리
        {
            'and': [condition1, condition2, ...],
            'or': [condition1, condition2, ...],
            'expression': {
                'left': column_name,
                'op': operator,
                'right': value
            }
        }

    Returns:
    --------
    Callable
        조건을 만족하는 마스크
    """
    # print(f'parse_conditions input: {conditions}')

    # 단일 expression 조건인 경우
    if 'expression' in conditions:
        return parse_expression(df, conditions['expression'])

    # and 조건인 경우
    if 'and' in conditions:
        conditions_list = conditions['and']
        if not conditions_list:
            raise ValueError('and 조건이 비어있습니다.')
        # 첫 번째 조건으로 시작
        result = parse_conditions(df, conditions_list[0])
        # 나머지 조건들과 and 연산
        for condition in conditions_list[1:]:
            result = result & parse_conditions(df, condition)
        return result

    # or 조건인 경우
    if 'or' in conditions:
        conditions_list = conditions['or']
        if not conditions_list:
            raise ValueError('or 조건이 비어있습니다.')
        # 첫 번째 조건으로 시작
        result = parse_conditions(df, conditions_list[0])
        # 나머지 조건들과 or 연산
        for condition in conditions_list[1:]:
            result = result | parse_conditions(df, condition)
        return result

    raise ValueError('조건이 올바르지 않습니다. and, or, expression 중 하나여야 합니다.')


def parse_expression(df: dd.DataFrame, condition: Dict[str, str]) -> Callable:
    op_map = {
        '==': operator.eq,
        '!=': operator.ne,
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
    }

    left = get_value(df, condition['left'])
    op = condition['op']
    right = get_value(df, condition.get('right', None))

    if op in op_map:
        return op_map[op](left, right)
    if op == 'isnull':
        return left.isnull()
    if op == 'not null':
        return ~left.isnull()
    if op == 'in':
        return left.isin(right)
    if op == 'not in':
        return ~left.isin(right)
    if op == 'startswith':
        return left.str.startswith(right)
    if op == 'not startswith':
        return ~left.str.startswith(right)
    if op == 'endswith':
        return left.str.endswith(right)
    if op == 'not endswith':
        return ~left.str.endswith(right)
    if op == 'contains':
        return left.str.contains(right, case=False)
    if op == 'not contains':
        return ~left.str.contains(right, case=False)
    if op == 'match':
        return left.str.match(right, case=False)
    if op == 'not match':
        return ~left.str.match(right, case=False)

    raise ValueError('조건이 올바르지 않습니다.')


def get_value(df: dd.DataFrame, v: Any) -> Any:
    """
    DataFrame의 컬럼 값 또는 상수 값을 반환하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    v : Any
        - dict 중 type이 있으면 type에 따라 처리
            type=value: 값으로 해석
            type=column: 컬럼명으로 해석
            type=function: 함수로 처리

    Returns:
    --------
    Any
        DataFrame 컬럼 또는 상수 값
    """

    if v is None:
        return None

    if isinstance(v, dict) and 'type' in v:
        if v['type'] == 'value':
            return get_value(df, v['value'])
        if v['type'] == 'column':
            return df[v['name']]
        if v['type'] == 'function':
            args = []
            kwargs = {}
            for v in v['args']:
                args.append(get_value(df, v))
            for k, v in v['kwargs'].items():
                kwargs[k] = get_value(df, v)
            return eval(f'{v['name']}(*{args}, **{kwargs})')

    if isinstance(v, list):
        vs = []
        for item in v:
            vs.append(get_value(df, item))
        return vs

    if isinstance(v, dict):
        vs = {}
        for k, v in v.items():
            vs[k] = get_value(df, v)
        return vs

    if isinstance(v, str):
        if not pattern_column_variable.search(v):
            return v
        else:
            return eval(pattern_column_variable.sub(r'df["\1"]', v))

    return v


def parse_value(df: dd.DataFrame, v: Any) -> Any:
    if v is None:
        return None

    if isinstance(v, int) or isinstance(v, float) or isinstance(v, bool):
        return v

    if isinstance(v, list):
        result = []
        for item in v:
            result.append(parse_value(df, item))
        return result

    if isinstance(v, dict):
        if 'type' not in v:
            return v
        else:
            if v['type'] == 'value':
                return v['value']
            if v['type'] == 'column':
                return df[v['name']]
            if v['type'] == 'function':
                return parse_function(
                    df,
                    v['name'],
                    v['args'] if 'args' in v else None,
                    v['kwargs'] if 'kwargs' in v else None,
                )

    raise_error_value()


def parse_function(df: dd.DataFrame, name: str, args: List[Any], kwargs: Dict[str, Any]) -> Any:
    if not args:
        args = parse_value(df, args)
    if not kwargs:
        kwargs = {k: parse_value(df, v) for k, v in kwargs.items()}

    if args and kwargs:
        return eval(f'{name}(*{args}, **{kwargs})')
    if args:
        return eval(f'{name}(*{args})')
    if kwargs:
        return eval(f'{name}(**{kwargs})')
    return eval(f'{name}()')
