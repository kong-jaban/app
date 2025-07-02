import numpy as np
from dask import dataframe as dd
from ups.dask.column_util import get_value, parse_conditions
from ups.dask.table import read_csv, read_parquet
from ups.run.params import call_params


def fill_by_mapping(
    df: dd.DataFrame,
    key_columns: list[str],
    map_key_columns: list[str],
    map_value_column: str,
    map_ds: dict,
    not_mapped_value: str = None,
    output_column: str = None,
) -> dd.DataFrame:
    """
    매핑 테이블에서 값을 가져와서 새로운 컬럼을 생성하는 함수

    Args:
        df (dask.dataframe): 원본 DataFrame
        key_columns (list): 매칭할 키 컬럼 이름 리스트
        map_key_columns (list): 매핑 테이블의 키 컬럼 이름 리스트
        map_value_column (str): 매핑 테이블에서 가져올 값 컬럼 이름
        map_ds : dict
            {type: csv or parquet, ...}
            ...: read_csv, read_parquet 인자 참조
        not_mapped_value (str): 매핑되지 않은 값 처리 방법
            None: 매핑되지 않은 값을 null로 처리
            str: 대체할 df의 컬럼명
        output_column (str): 결과를 저장할 컬럼 이름

    Returns:
        dask.dataframe: 새로운 컬럼이 추가된 DataFrame
    """
    # 키 컬럼과 매핑 키 컬럼의 개수가 일치하는지 확인
    if len(key_columns) != len(map_key_columns):
        raise ValueError("키 컬럼의 개수가 일치하지 않습니다.")

    # 매핑테이블 읽기
    if map_ds['datasource']['type'] == 'parquet':
        params = call_params('read_parquet', map_ds)
        df_map = read_parquet(**params)
    elif map_ds['datasource']['type'] == 'csv':
        params = call_params('read_csv', map_ds)
        df_map = read_csv(**params)
    else:
        raise ValueError(
            f'지원하는 데이터 소스 타입: parquet, csv ({map_ds["datasource"]["type"]}은 지원하지 않습니다.)'
        )

    # 매핑 테이블에서 필요한 컬럼만 선택
    df_map = df_map[map_key_columns + [map_value_column]]
    df_map = df_map.drop_duplicates(keep='first')
    if output_column is None:
        output_column = map_value_column
    else:
        df_map = df_map.rename(columns={map_value_column: output_column})

    if not_mapped_value is not None:
        df_org = df[output_column].copy() if output_column == not_mapped_value else df[not_mapped_value]

    # 원본 DataFrame과 매핑 테이블을 키 컬럼으로 조인
    df = df.merge(df_map, left_on=key_columns, right_on=map_key_columns, how='left')

    #
    if df_org is not None:
        df[output_column] = df[output_column].fillna(df_org)

    return df


def apply_conditions(
    df: dd.DataFrame,
    data_type: str = 'string',
    output_column: str = None,
    conditions: list[dict] = None,
    default_value: dict = None,
) -> dd.DataFrame:
    """
    조건에 따라 컬럼을 처리하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    data_type : str, default='string'
        처리 결과 컬럼 타입
    output_columns : str or list, default=None
        처리 결과 컬럼 이름 또는 이름들의 리스트
        None일 경우 원본 컬럼 이름 사용
    conditions : list of dict
        조건과 처리 함수를 정의한 딕셔너리들의 리스트
        각 딕셔너리는 다음 키를 포함:
        - 'condition': 조건식
        - 'value': 조건에 맞으면 할당할 값
    default : Any, default=None
        조건에 해당하지 않는 경우의 처리
        - str, number, bool, list, dict: 값
        - dict 중 type이 있으면 type에 따라 처리
            type=value: 값으로 해석
            type=column: 컬럼명으로 해석
            type=function: 함수로 처리

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame

    Examples:
    --------
    """

    conds = []
    values = []
    for condition in conditions:
        values.append(get_value(df, condition['value']))
        conds.append(parse_conditions(df, condition['condition']))

    default_value = get_value(df, default_value)

    def _apply(dx):
        dx = np.select(conds, values, default_value)
        return dx

    df[output_column] = df[output_column].map_partitions(_apply, meta=(output_column, data_type))
    return df
