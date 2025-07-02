import io
from pathlib import Path
import shutil
import dask.dataframe as dd
import re
from typing import Callable, Dict, Tuple, Union, List, Literal

# pip install msoffcrypto-tool
import msoffcrypto

import pandas as pd
from ups.dask.column_util import parse_conditions
from ups.dask.valid_check import (
    str_to_list,
    valid_check_column_exists,
    valid_check_datasource_type,
    valid_check_drop_keep,
    valid_check_join_type,
    valid_check_na_position,
)
from ups.run.params import call_params
from ups.util.progress_callback import ProgressCallback


def remove_or_error(path: Path, overwrite: bool = True) -> None:
    path = Path(path)

    if not path.exists():
        return

    if not overwrite:
        raise FileExistsError(f'파일이 이미 존재합니다: {path}')

    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def read_parquet(
    path: str = None,
    **kwargs,
) -> dd.DataFrame:
    """
    Dask를 사용하여 Parquet 파일을 읽는 함수

    Parameters:
    -----------
    path : str
        Parquet 파일 또는 디렉토리 경로
    **kwargs :
        dd.read_parquet에 전달할 추가 매개변수

    Returns:
    --------
    dask.dataframe.DataFrame
        Dask DataFrame 객체
    """

    df = dd.read_parquet(path, **kwargs)
    return df


def write_parquet(
    df: dd.DataFrame,
    path: str = None,
    write_index: bool = False,
    overwrite: bool = True,
    columns: List[str] = None,
    callback: Callable = None,
    **kwargs,
) -> None:
    """
    Dask DataFrame을 Parquet 파일로 저장하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        저장할 Dask DataFrame
    path : str
        저장할 경로 및 파일명
    write_index : bool, default=False
        인덱스 저장 여부
    overwrite : bool, default=True
        기존 파일 덮어쓰기 여부
    columns : list, default=None
        저장할 컬럼 리스트
    callback : Callable, default=None
        progress 콜백 함수
    **kwargs :
        dd.to_parquet에 전달할 추가 매개변수

    Returns:
    --------
    None
    """
    if columns:
        # 존재하지 않는 컬럼 확인
        valid_check_column_exists(df, columns)

    remove_or_error(path, overwrite)

    df = df[columns] if columns else df

    if callback:
        with ProgressCallback(callback=callback):
            df.to_parquet(path, write_index=write_index, **kwargs)
    else:
        df.to_parquet(path, write_index=write_index, **kwargs)

    return


def read_csv(
    path: str = None,
    sep: str = ',',
    encoding: str = 'utf-8',
    header: int = 0,
    **kwargs,
) -> dd.DataFrame:
    """
    Dask를 사용하여 CSV 파일을 읽는 함수

    Parameters:
    -----------
    path : str
        CSV 파일의 경로
    sep : str, default=','
        CSV 파일의 구분자
    encoding : str, default='utf-8'
        CSV 파일의 인코딩
    header : int, default=0
        CSV 파일의 헤더 행 번호
    callback : Callable, default=None
        progress 콜백 함수
    **kwargs :
        dd.read_csv에 전달할 추가 매개변수

    Returns:
    --------
    dask.dataframe.DataFrame
        Dask DataFrame 객체
    """

    df = dd.read_csv(path, sep=sep, encoding=encoding, header=header, **kwargs)
    return df


def write_csv(
    df: dd.DataFrame,
    path: str = None,
    single_file: bool = True,
    sep: str = ',',
    encoding: str = 'utf-8',
    header: bool = True,
    index: bool = False,
    columns: List[str] = None,
    callback: Callable = None,
    **kwargs,
) -> None:
    """
    Dask DataFrame을 CSV 파일로 저장하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        저장할 Dask DataFrame
    path : str
        저장할 경로 및 파일명
    single_file : bool, default=True
        True일 경우 하나의 파일로 저장
        False일 경우 파티션별로 여러 파일 저장
    sep : str, default=','
        CSV 파일의 구분자
    encoding : str, default='utf-8'
        CSV 파일의 인코딩
    header : bool, default=True
        헤더 저장 여부
    index : bool, default=False
        인덱스 저장 여부
    columns : list, default=None
        저장할 컬럼 리스트
    callback : Callable, default=None
        progress 콜백 함수
    **kwargs :
        dd.to_csv에 전달할 추가 매개변수

    Returns:
    --------
    None
    """
    if columns:
        # 존재하지 않는 컬럼 확인
        valid_check_column_exists(df, columns)

    remove_or_error(path, True)

    df = df[columns] if columns else df

    if callback:
        with ProgressCallback(callback=callback):
            df.to_csv(
                path,
                single_file=single_file,
                sep=sep,
                encoding=encoding,
                header=header,
                index=index,
                **kwargs,
            )
    else:
        df.to_csv(
            path,
            single_file=single_file,
            sep=sep,
            encoding=encoding,
            header=header,
            index=index,
            **kwargs,
        )
    return


def read_excel(
    path: str = None,
    sheet_name: str = None,
    header: int = 0,
    skiprows: Union[int, List[int]] = 0,
    password: str = None,
    npartitions: int = 20,
    **kwargs,
) -> dd.DataFrame:
    """
    Dask를 사용하여 Excel 파일을 읽는 함수

    Parameters:
    -----------
    path : str
        Excel 파일의 경로
    sheet_name : str
        Excel 파일의 시트 이름
    header : int, default=0
        Excel 파일의 헤더 행 번호 (0 based)
        None: 헤더 없음
    skiprows : int or list, default=0
        Excel 파일의 건너뛸 행 번호
        int: 건너뛸 행 번호
        list: 건너뛸 행 번호 리스트
    password : str, default=None
        Excel 파일의 비밀번호
    npartitions : int, default=10
        Dask DataFrame의 파티션 수
    **kwargs :
        dd.read_excel에 전달할 추가 매개변수

    Returns:
    --------
    dask.dataframe.DataFrame
        Dask DataFrame 객체
    """
    # skiprows가 float인 경우 int로 변환
    if isinstance(skiprows, float):
        skiprows = int(skiprows)

    if not password:
        with pd.ExcelFile(path) as f:
            pdf = pd.read_excel(f, sheet_name=sheet_name, header=header, skiprows=skiprows, **kwargs)
    else:
        with open(path, 'rb') as f:
            decrypted = io.BytesIO()
            f = msoffcrypto.OfficeFile(f)
            f.load_key(password)
            f.decrypt(decrypted)
            pdf = pd.read_excel(
                decrypted,
                sheet_name=sheet_name,
                header=header,
                skiprows=skiprows,
                **kwargs,
            )

    df = dd.from_pandas(pdf, npartitions=npartitions)
    return df


def drop_columns(
    df: dd.DataFrame,
    columns: Union[str, List[str]] = None,
    pattern: str = None,
) -> dd.DataFrame:
    """
    DataFrame에서 특정 컬럼들을 삭제하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : str or list, default=None
        삭제할 컬럼 이름 또는 이름들의 리스트
    pattern : str, default=None
        정규식 패턴으로 삭제할 컬럼 선택 (예: 'temp_.*' -> temp_로 시작하는 모든 컬럼)

    Returns:
    --------
    dask.dataframe.DataFrame
        컬럼이 삭제된 DataFrame
    """
    columns_to_drop = []

    # 패턴으로 컬럼 선택
    if pattern:
        pattern_regex = re.compile(pattern)
        columns_to_drop.extend([col for col in df.columns if pattern_regex.match(col)])

    # 직접 지정한 컬럼 추가
    if columns:
        if isinstance(columns, str):
            columns = [columns]
        columns_to_drop.extend(columns)

    # 중복 제거
    columns_to_drop = list(dict.fromkeys(columns_to_drop))

    # 존재하지 않는 컬럼 확인
    valid_check_column_exists(df, columns_to_drop)

    # 모든 컬럼을 삭제하려는 경우 검증
    if len(columns_to_drop) == len(df.columns):
        raise ValueError('모든 컬럼을 삭제할 수 없습니다.')

    # 컬럼 삭제
    df = df.drop(columns=columns_to_drop)
    return df


def select_columns(
    df: dd.DataFrame,
    columns: Union[str, List[str]] = None,
    pattern: str = None,
    exclude: Union[str, List[str]] = None,
) -> dd.DataFrame:
    """
    DataFrame에서 특정 컬럼들을 선택하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : str or list, default=None
        선택할 컬럼 이름 또는 이름들의 리스트
    pattern : str, default=None
        정규식 패턴으로 컬럼 선택 (예: 'user_.*' -> user_로 시작하는 모든 컬럼)
    exclude : str or list, default=None
        제외할 컬럼 이름 또는 이름들의 리스트

    Returns:
    --------
    dask.dataframe.DataFrame
        선택된 컬럼들로 구성된 DataFrame
    """
    selected_columns = []

    # 패턴으로 컬럼 선택
    if pattern:
        pattern_regex = re.compile(pattern)
        selected_columns.extend([col for col in df.columns if pattern_regex.match(col)])

    # 직접 지정한 컬럼 추가
    if columns:
        if isinstance(columns, str):
            columns = [columns]
        selected_columns.extend(columns)
        # 중복 제거
        selected_columns = list(dict.fromkeys(selected_columns))

    # 패턴과 컬럼 모두 지정되지 않은 경우 모든 컬럼 반환
    if not pattern and not columns:
        selected_columns = df.columns.tolist()

    # 제외할 컬럼 처리
    if exclude:
        if isinstance(exclude, str):
            exclude = [exclude]
        selected_columns = [col for col in selected_columns if col not in exclude]

    # 선택 컬럼 없음
    if not selected_columns:
        raise ValueError('선택한 컬럼이 없습니다.')

    # 존재하지 않는 컬럼 확인
    valid_check_column_exists(df, selected_columns)

    return df[selected_columns]


def rename_columns(
    df: dd.DataFrame,
    columns: Dict[str, str] = None,
    pattern: Dict[str, str] = None,
) -> dd.DataFrame:
    """
    DataFrame의 컬럼 이름을 변경하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : dict
        변경할 컬럼 이름 매핑
        {'old_name': 'new_name', ...}
    pattern : dict, default=None
        정규식 패턴으로 컬럼 이름 변경
        find: 찾을 패턴
        replace: 대체할 텍스트
        {find: 'temp_(.+)', replace='new_\1'}

    Returns:
    --------
    dask.dataframe.DataFrame
        컬럼 이름이 변경된 DataFrame
    """
    # 패턴 기반 이름 변경
    if pattern:
        all_columns = list(df.columns)
        pattern_regex = re.compile(pattern['find'])

        # 패턴에 매칭되는 모든 컬럼에 대해 이름 변경
        pattern_renames = {}
        for col in all_columns:
            if pattern_regex.match(col):
                new_name = pattern_regex.sub(pattern['replace'], col)
                pattern_renames[col] = new_name

        # 기존 매핑과 병합
        if columns:
            columns.update(pattern_renames)
        else:
            columns = pattern_renames

    # 변경할 컬럼이 없는 경우
    if not columns:
        return df

    # 존재하지 않는 컬럼 확인
    valid_check_column_exists(df, list(columns.keys()))

    # 중복되는 새 이름 확인
    new_names = list(columns.values())
    if len(new_names) != len(set(new_names)):
        raise ValueError('새로운 컬럼 이름에 중복이 있습니다.')

    # 컬럼 이름 변경
    df = df.rename(columns=columns)
    return df


def drop_duplicates(
    df: dd.DataFrame,
    columns: Union[str, List[str]] = None,
    keep: Literal['first', 'last', 'nothing'] = 'first',
    sort_order: Dict[str, Literal['asc', 'desc']] = None,
) -> dd.DataFrame:
    """
    DataFrame에서 중복 제거된 고유한 행을 반환하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : str or list, default=None
        중복 확인할 컬럼 이름 또는 이름들의 리스트
        None일 경우 모든 컬럼 사용
    keep : str, default='first'
        중복된 행 중 어떤 것을 유지할지 지정
        'first': 첫 번째 행 유지
        'last': 마지막 행 유지
        'nothing': 남기지 않음
    sort_order : dict
        정렬 기준이 되는 컬럼 이름과 오름차순 여부 리스트
        {'column1': 'ascending', 'column2': 'descending', ...]
        정렬 순서
        - ascending: 오름차순
        - descending: 내림차순

    Returns:
    --------
    dask.dataframe.DataFrame
        중복이 제거된 DataFrame
    """
    columns = str_to_list(columns)
    keep = valid_check_drop_keep(keep)
    if keep == 'nothing':
        keep = None

    # 정렬 후 중복 제거
    if sort_order and columns:
        df = orderby(df, by=sort_order, na_position='last')

    # 중복 제거
    if columns:
        # 특정 컬럼들에 대해서만 중복 제거
        df = df.drop_duplicates(subset=columns, keep=keep, ignore_index=True)
    else:
        # 모든 컬럼에 대해 중복 제거
        df = df.drop_duplicates(keep=keep, ignore_index=True)

    return df


def filter(
    df: dd.DataFrame,
    conditions: Dict[Literal['ops', 'and', 'or'], Union[Dict, List]] = None,
) -> dd.DataFrame:
    """
    DataFrame에 여러 조건을 적용하여 필터링하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        필터링할 Dask DataFrame
    condition : dict
        필터링 조건
        {
            'ops': {
                'left': column_name,
                'op': operator,
                'right': value
            },
            'and': [condition1, condition2, ...],
            'or': [condition1, condition2, ...]
        }

    Returns:
    --------
    dask.dataframe.DataFrame
        필터링된 DataFrame
    """
    if not conditions:
        raise ValueError('필터링 조건이 없습니다.')

    mask = parse_conditions(df, conditions)
    return df[mask]


def orderby(
    df: dd.DataFrame,
    by: Dict[str, Literal['asc', 'desc']] = None,
    na_position: Literal['first', 'last'] = 'last',
) -> dd.DataFrame:
    """
    DataFrame을 특정 컬럼 기준으로 정렬하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    by : dict
        정렬 기준이 되는 컬럼 이름과 오름차순 여부 리스트
        {'column1': 'ascending', 'column2': 'descending', ...]
        정렬 순서
        - asc: 오름차순
        - desc: 내림차순
    na_position : str, default='last'
        NA 값의 위치
        - 'last': NA 값을 마지막에 위치
        - 'first': NA 값을 처음에 위치

    Returns:
    --------
    dask.dataframe.DataFrame
        정렬된 DataFrame
    """
    valid_check_column_exists(df, list(by.keys()))
    na_position = valid_check_na_position(na_position)

    # 정렬 수행
    df = df.sort_values(
        by=[c for c in by.keys()],
        ascending=[x.lower() == 'asc' for x in by.values()],
        na_position=na_position,
    )

    return df


def union(
    left_df: dd.DataFrame,
    right_ds: Dict[str, str] = None,
    ignore_index: bool = True,
    column_sort: bool = False,
) -> dd.DataFrame:
    """
    여러 DataFrame을 행 방향으로 합치는 함수 (중복 포함)

    Parameters:
    -----------
    left_df : dask.dataframe.DataFrame
        왼쪽 DataFrame
    right_ds : dict
        {type: csv or parquet, ...}
        ...: read_csv, read_parquet 인자 참조
    ignore_index : bool, default=True
        True일 경우 기존 인덱스를 무시하고 새로운 인덱스 생성
    column_sort : bool, default=False
        True일 경우 컬럼을 알파벳 순으로 정렬

    Returns:
    --------
    dask.dataframe.DataFrame
        합쳐진 DataFrame
    """
    ds_type = valid_check_datasource_type(right_ds['datasource']['type'])

    # 오른쪽 DataFrame 읽기
    if ds_type == 'parquet':
        params = call_params('read_parquet', right_ds)
        right_df = read_parquet(**params)
    elif ds_type == 'csv':
        params = call_params('read_csv', right_ds)
        right_df = read_csv(**params)

    # 컬럼 검증
    for ii, c in enumerate(zip(left_df.columns.tolist(), right_df.columns.tolist())):
        if c[0] != c[1]:
            raise ValueError(f'{ii}번째 컬럼이 일치하지 않습니다.')

    # DataFrame 합치기
    df = dd.concat(
        [left_df, right_df],
        axis=0,  # 행 방향으로 합치기
        ignore_index=ignore_index,
        sort=column_sort,
    )

    return df


def join(
    left_df: dd.DataFrame,
    right_ds: Dict[str, str] = None,
    how: Literal['inner', 'left', 'right', 'outer'] = 'inner',
    left_on: Union[str, List[str]] = None,
    right_on: Union[str, List[str]] = None,
    suffixes: Tuple[str, str] = ('_x', '_y'),
):
    """
    두 DataFrame을 조인하는 함수

    Parameters:
    -----------
    left_df : dask.dataframe.DataFrame
        왼쪽 DataFrame
    right_ds : dict
        {type: csv or parquet, ...}
        ...: read_csv, read_parquet 인자 참조
    on : str or list, default=None
        양쪽 DataFrame에서 조인할 컬럼 이름 또는 이름들의 리스트
    how : str, default='inner'
        조인 방식 ('inner', 'left', 'right', 'outer')
    left_on : str or list, default=None
        왼쪽 DataFrame에서 조인할 컬럼 이름 또는 이름들의 리스트
    right_on : str or list, default=None
        오른쪽 DataFrame에서 조인할 컬럼 이름 또는 이름들의 리스트
    suffixes : tuple, default=('_x', '_y')
        중복되는 컬럼 이름에 붙일 접미사

    Returns:
    --------
    dask.dataframe.DataFrame
        조인된 DataFrame
    """
    left_on = str_to_list(left_on)
    right_on = str_to_list(right_on)
    how = valid_check_join_type(how)
    ds_type = valid_check_datasource_type(right_ds['datasource']['type'])

    # 오른쪽 DataFrame 읽기
    if ds_type == 'parquet':
        params = call_params('read_parquet', right_ds)
        right_df = read_parquet(**params)
    elif ds_type == 'csv':
        params = call_params('read_csv', right_ds)
        right_df = read_csv(**params)

    # 조인 수행
    df = left_df.merge(right_df, left_on=left_on, right_on=right_on, how=how, suffixes=suffixes)

    return df


def make_map_groupby_count(
    df: dd.DataFrame,
    group_columns: Union[str, List[str]] = None,
    count_column: Union[str, None] = None,
    sort_by_count: bool = False,
    ascending: bool = True,
) -> dd.DataFrame:
    """
    지정된 컬럼으로 그룹화하고 카운트하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    group_columns : str or list
        그룹화할 컬럼 이름 또는 이름들의 리스트
    count_column : str, default=None
        카운트할 특정 컬럼. None일 경우 전체 행 카운트
    sort_by_count : bool, default=True
        결과를 카운트 기준으로 정렬할지 여부
    ascending : bool, default=False
        정렬 순서 (False: 내림차순, True: 오름차순)

    Returns:
    --------
    dask.dataframe.DataFrame
        그룹화되고 카운트된 결과 DataFrame
    """
    group_columns = str_to_list(group_columns)

    # 그룹화 및 카운트
    if count_column is None:
        df = df.groupby(group_columns).size()
    else:
        df = df.groupby(group_columns)[count_column].count()

    df = df.reset_index().rename(columns={0: 'count'})

    # 정렬
    if sort_by_count:
        df = df.sort_values('count', ascending=ascending, na_position='first')
    else:
        df = df.sort_values(group_columns, ascending=ascending, na_position='first')

    return df


def cast_data_type(
    df: dd.DataFrame,
    columns: Dict[str, str] = None,
) -> dd.DataFrame:
    """
    DataFrame의 컬럼 타입을 변환하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : dict
        {column: type, ...}

    Returns:
    --------
    dask.dataframe.DataFrame
        타입이 변환된 DataFrame
    """

    return df.astype(columns)
