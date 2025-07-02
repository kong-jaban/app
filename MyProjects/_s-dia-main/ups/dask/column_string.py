import re
from typing import Literal, Union

import dask.dataframe as dd

from ups.dask.valid_check import (
    str_to_list,
    valid_check_column_count,
    valid_check_string_case,
    valid_check_substring_start_end,
)


def to_upper(
    df: dd.DataFrame,
    columns: Union[str, list],
    output_columns: Union[str, list] = None,
) -> dd.DataFrame:
    return change_case(df, columns, output_columns, case='upper')


def to_lower(
    df: dd.DataFrame,
    columns: Union[str, list],
    output_columns: Union[str, list] = None,
) -> dd.DataFrame:
    return change_case(df, columns, output_columns, case='lower')


def change_case(
    df: dd.DataFrame,
    columns: Union[str, list],
    output_columns: Union[str, list] = None,
    case: Literal['upper', 'lower', 'title', 'capitalize'] = 'upper',
) -> dd.DataFrame:
    """
    문자열 컬럼을 대소문자로 변환하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : str or list
        대문자로 변환할 컬럼 이름 또는 이름들의 리스트
    output_columns : str or list, default=None
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
        None일 경우 원본 컬럼을 덮어씀
    case : str, default='upper'
        'upper' : 대문자로 변환
        'lower' : 소문자로 변환
        'title' : 첫 글자만 대문자로 변환
        'capitalize' : 각 단어의 첫 글자만 대문자로 변환

    Returns:
    --------
    dask.dataframe.DataFrame
        대문자로 변환된 DataFrame
    """
    columns = str_to_list(columns)
    output_columns = columns if output_columns is None else str_to_list(output_columns)

    valid_check_column_count(columns, output_columns)
    case = valid_check_string_case(case)

    # 대소문자 변환 함수 선택
    def _apply(s, case):
        if case == 'upper':
            return s.str.upper()
        if case == 'lower':
            return s.str.lower()
        if case == 'title':
            return s.str.title()
        if case == 'capitalize':
            return s.str.capitalize()

    # 각 컬럼에 대해 대문자 변환 수행
    for col, out_col in zip(columns, output_columns):
        df[col] = df[col].astype('object')
        df[out_col] = df[col].map_partitions(_apply, case=case, meta=(out_col, 'object'))

    return df


def substring(
    df: dd.DataFrame,
    columns: Union[str, list],
    output_columns: Union[str, list] = None,
    start: Union[int, str] = None,
    end: Union[int, str] = None,
) -> dd.DataFrame:
    """
    문자열 컬럼에서 부분 문자열을 추출하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : str or list
        부분 문자열을 추출할 컬럼 이름 또는 이름들의 리스트
    output_columns : str or list, default=None
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
        None일 경우 원본 컬럼을 덮어씀
    start : int, default=None
        시작 위치 (0부터 시작, 음수 인덱스 가능)
        None일 경우 처음부터 시작
    end : int, default=None
        끝 위치 (이 위치는 포함되지 않음, 음수 인덱스 가능)
        None일 경우 끝까지 추출

    Returns:
    --------
    dask.dataframe.DataFrame
        부분 문자열이 추출된 DataFrame
    """
    columns = str_to_list(columns)
    output_columns = columns if output_columns is None else str_to_list(output_columns)
    valid_check_column_count(columns, output_columns)
    valid_check_substring_start_end(start)
    valid_check_substring_start_end(end)

    # 문자열 타입으로 변환
    df[columns] = df[columns].astype(str)

    # dask에서 음수 인덱스 지원하지 않음
    # df[output_column] = df[column].str.slice(start, end)

    for col, out_col in zip(columns, output_columns):
        df[out_col] = df[col].map_partitions(lambda s: s.str[start:end], meta=(out_col, 'object'))
    return df


def replace_string(
    df: dd.DataFrame,
    columns: Union[str, list] = None,
    replacements: Union[dict, list] = None,
    output_columns: Union[str, list] = None,
    use_regex: bool = False,
    ignore_case: bool = True,
) -> dd.DataFrame:
    """
    문자열 컬럼에서 특정 텍스트를 다른 텍스트로 치환하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : str or list
        치환을 수행할 컬럼 이름 또는 이름들의 리스트
    replacements : dict or list of tuple
        치환할 패턴과 대체 텍스트의 딕셔너리
        예: {'old': 'new'}
    output_columns : str or list, default=None
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
        None일 경우 원본 컬럼을 덮어씀
    use_regex : bool, default=False
        True일 경우 정규식 패턴 사용
    ignore_case : bool, default=True
        True일 경우 대소문자 구분 없이 치환

    Returns:
    --------
    dask.dataframe.DataFrame
        텍스트가 치환된 DataFrame
    """
    columns = str_to_list(columns)
    output_columns = columns if output_columns is None else str_to_list(output_columns)
    valid_check_column_count(columns, output_columns)

    def _apply(s):
        use_regex2 = True if ignore_case else use_regex
        for old_text, new_text in replacements.items():
            if ignore_case:
                old_text = f'(?i){old_text}' if use_regex else f'(?i){re.escape(old_text)}'
                new_text = new_text if use_regex else re.escape(new_text)
            s = s.str.replace(old_text, new_text, regex=use_regex2)
        return s

    # 문자열 타입으로 변환
    df[columns] = df[columns].astype(str)

    # 결과 저장
    for col, out_col in zip(columns, output_columns):
        df[out_col] = df[col].map_partitions(_apply, meta=(out_col, 'object'))
    return df


def combine_columns(
    df: dd.DataFrame,
    columns: Union[str, list] = None,
    output_column: Union[str, list] = None,
    sep: str = '',
    drop_originals: bool = False,
) -> dd.DataFrame:
    """
    여러 컬럼을 하나의 문자열 컬럼으로 합치는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : list
        합칠 컬럼들의 이름 리스트
    output_column : str
        결과 컬럼의 이름
    sep : str, default=' '
        컬럼들을 합칠 때 사용할 구분자
    drop_originals : bool, default=False
        True일 경우 원본 컬럼들을 삭제

    Returns:
    --------
    dask.dataframe.DataFrame
        컬럼이 합쳐진 Dask DataFrame
    """

    def _func(df):
        return df[columns].astype(str).agg(sep.join, axis=1)

    df[output_column] = df.map_partitions(_func, meta=(output_column, 'object'))

    # 원본 컬럼 삭제 옵션
    if drop_originals:
        df = df.drop(columns=list(filter(lambda x: x != output_column, columns)))

    return df
