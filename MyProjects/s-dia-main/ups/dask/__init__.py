import importlib
import dask.dataframe as dd
from .column_date import (
    date_add,
    date_diff,
)

from .column_encrypt import (
    blake,
    sha,
    shake,
)

from .column_mix import (
    fill_by_mapping,
    apply_conditions,
)

from .column_numeric import (
    categorize_by_equal_width,
    categorize_by_interval,
    categorize_by_unit,
    fill_random_float,
    fill_random_int,
    fill_random_normal,
    fill_random_sequence,
    round,
    round_down,
    round_up,
    rounding,
    top_bottom_15iqr,
    top_bottom_3sigma,
    top_bottom_coding,
    top_bottom_percentile,
    truncate_to_left,
)

from .column_string import (
    change_case,
    combine_columns,
    replace_string,
    substring,
    to_lower,
    to_upper,
)

from .table import (
    cast_data_type,
    drop_columns,
    drop_duplicates,
    filter,
    join,
    make_map_groupby_count,
    read_csv,
    read_parquet,
    rename_columns,
    select_columns,
    orderby,
    union,
    write_csv,
    write_parquet,
)

from .distribution import (
    get_distribution,
    get_number_outlier,
)


def call_function(function_name: str, df: dd.DataFrame, **kwargs):
    """
    함수를 동적으로 호출하는 함수. 모듈을 자동으로 찾아서 호출합니다.

    Parameters:
    -----------
    function_name : str
        호출할 함수 이름
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    **kwargs : dict
        함수에 전달할 키워드 인자들

    Returns:
    --------
    함수의 반환값

    Examples:
    --------
    # round 함수 호출
    result = call_function('round', df, columns='value', decimals=2)

    # to_upper 함수 호출
    result = call_function('to_upper', df, columns='name')
    """
    # 사용 가능한 모듈 목록
    modules = [
        'column_numeric',
        'column_string',
        'column_date',
        'column_encrypt',
        'column_mix',
        'table',
        'distribution',
    ]

    for module_name in modules:
        # try:
        # 모듈 가져오기
        mod = importlib.import_module(f'ups.dask.{module_name}')
        # 함수가 모듈에 있는지 확인
        if hasattr(mod, function_name):
            func = getattr(mod, function_name)
            if function_name in ['read_csv', 'read_parquet']:
                return func(**kwargs)
            else:
                return func(df, **kwargs)

    #     except (ImportError, AttributeError):
    #         continue
    #     except Exception as e:
    #         raise Exception(f'함수 호출 중 오류가 발생했습니다: {str(e)}')

    raise ValueError(f'함수를 찾을 수 없습니다: {function_name}')


__all__ = [
    #
    'call_function',
    # Column: Date 함수
    'date_add',
    'date_diff',
    # Column: Encrypt 함수
    'blake',
    'sha',
    'shake',
    # Column: Mix 함수
    'fill_by_mapping',
    'apply_conditions',
    # Column: Numeric 함수
    'categorize_by_equal_width',
    'categorize_by_interval',
    'categorize_by_unit',
    'fill_random_float',
    'fill_random_int',
    'fill_random_normal',
    'fill_random_sequence',
    'round',
    'round_down',
    'round_up',
    'rounding',
    'top_bottom_15iqr',
    'top_bottom_3sigma',
    'top_bottom_coding',
    'top_bottom_percentile',
    'truncate_to_left',
    # Column: String 함수
    'change_case',
    'combine_columns',
    'replace_string',
    'substring',
    'to_lower',
    'to_upper',
    # Table 함수
    'cast_data_type',
    'drop_columns',
    'drop_duplicates',
    'filter',
    'join',
    'make_map_groupby_count',
    'read_csv',
    'read_parquet',
    'rename_columns',
    'select_columns',
    'orderby',
    'union',
    'write_csv',
    'write_parquet',
    # Distribution 함수
    'get_distribution',
    'get_number_outlier',
]
