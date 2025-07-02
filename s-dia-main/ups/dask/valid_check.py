import dask.dataframe as dd
from typing import Any, Union


# 타입 힌트 때문에 Code is unreachable 나오지만
# 타입 힌트는 실행 시 영향이 없으므로 에러 처리 코드 있어야 함


def str_to_list(x: Union[str, list]) -> list:
    if isinstance(x, str):
        return [x]
    elif isinstance(x, list):
        return x
    else:
        # 타입 힌트는 실행 시 영향이 없으므로 에러 처리 코드 있어야 함
        raise ValueError(f'입력값은 문자열 또는 리스트여야 합니다: {x}')


def raise_error_datetime(x: str) -> None:
    raise ValueError(f'존재하지 않는 컬럼이거나 형식에 맞지 않는 datetime 지정입니다: {x}')


def raise_error_value() -> None:
    raise ValueError('입력값은 컬럼명 또는 딕셔너리여야 합니다.')


def valid_check_datasource_type(x: str) -> str:
    if isinstance(x, str):
        x = x.lower()
        valid_datasource_types = ['parquet', 'csv']
        if x in valid_datasource_types:
            return x
    raise ValueError(f'지원하지 않는 데이터소스 타입입니다. 지원 타입: {valid_datasource_types}: {x}')


def valid_check_column_integer(df: dd.DataFrame, x: str) -> None:
    if (not isinstance(x, str)) or (df[x].dtype.kind != 'i'):
        raise ValueError(f'정수형 컬럼이 아닙니다: {x}')


def valid_check_drop_keep(x: str) -> str:
    if isinstance(x, str):
        x = x.lower()
        valid_drop_keep = ['first', 'last', 'nothing']
        if x in valid_drop_keep:
            return x

    raise ValueError(f'keep은 {", ".join(valid_drop_keep)} 중 하나여야 합니다: {x}')


def valid_check_join_type(x: str) -> str:
    # 조인 방식 검증
    if isinstance(x, str):
        x = x.lower()
        valid_joins = {'inner', 'left', 'right', 'outer'}
        if x in valid_joins:
            return x
    raise ValueError(f'지원하지 않는 조인 방식입니다. 지원 방식: {valid_joins}: {x}')


def valid_check_column_count(left: list, right: list) -> None:
    # 컬럼 개수 검증
    if (not isinstance(left, list)) or (not isinstance(right, list)) or (len(left) != len(right)):
        raise ValueError('입력 컬럼과 출력 컬럼의 개수가 일치하지 않습니다.')


def valid_check_column_exists(df: dd.DataFrame, columns: list) -> None:
    if not isinstance(df, dd.DataFrame):
        # 타입 힌트는 실행 시 영향이 없으므로 에러 처리 코드 있어야 함
        raise ValueError('입력값은 Dask DataFrame이어야 합니다.')

    if (not isinstance(columns, list)) or (len(columns) == 0):
        raise ValueError('컬럼 목록이 아니거나, 빈 컬럼 목록입니다.')

    # 존재하지 않는 컬럼 확인
    non_existent = [col for col in columns if col not in df.columns]
    if non_existent:
        raise ValueError(f'존재하지 않는 컬럼입니다: {non_existent}')


def valid_check_encoding(x: str) -> str:
    if isinstance(x, str):
        x = x.lower()
        valid_encodings = ['hex_lower', 'hex_upper', 'base64']
        if x in valid_encodings:
            return x
    raise ValueError(f'encoding은 {", ".join(valid_encodings)} 중 하나여야 합니다: {x}')


def valid_check_salt_position(x: str) -> str:
    if isinstance(x, str):
        x = x.lower()
        valid_salt_positions = ['prefix', 'suffix']
        if x in valid_salt_positions:
            return x
    raise ValueError(f'salt_position은 {", ".join(valid_salt_positions)} 중 하나여야 합니다: {x}')


def valid_check_sha_algorithm(x: str) -> str:
    if isinstance(x, str):
        x = x.lower()
        valid_algorithms = ['sha2', 'sha3']
        if x in valid_algorithms:
            return x
    raise ValueError(f'algorithm은 {", ".join(valid_algorithms)} 중 하나여야 합니다: {x}')


def valid_check_sha_length(x: int) -> None:
    if isinstance(x, int):
        valid_lengths = [224, 256, 384, 512]
        if x in valid_lengths:
            return x
    raise ValueError(f'length는 {", ".join(map(str, valid_lengths))} 중 하나여야 합니다: {x}')


def valid_check_shake_algorithm(x: str) -> str:
    if isinstance(x, str):
        x = x.lower()
        valid_algorithms = ['shake_128', 'shake_256']
        if x in valid_algorithms:
            return x
    raise ValueError(f'algorithm은 {", ".join(valid_algorithms)} 중 하나여야 합니다: {x}')


def valid_check_shake_length(x: int) -> None:
    if (not isinstance(x, int)) or (x < 1):
        raise ValueError('length는 1 이상의 숫자여야 합니다.')


def valid_check_blake_algorithm(x: str) -> str:
    if isinstance(x, str):
        x = x.lower()
        valid_algorithms = ['blake2b', 'blake2s']
        if x in valid_algorithms:
            return x
    raise ValueError(f'algorithm은 {", ".join(valid_algorithms)} 중 하나여야 합니다: {x}')


def valid_check_blake2s_length(x: int) -> None:
    if (not isinstance(x, int)) or (x < 1) or (x > 32):
        raise ValueError('length는 1 - 32 사이 숫자여야 합니다.')


def valid_check_blake2b_length(x: int) -> None:
    if (not isinstance(x, int)) or (x < 1) or (x > 64):
        raise ValueError('length는 1 - 64 사이 숫자여야 합니다.')


def valid_check_multiplier(x: Union[int, float]) -> None:
    if (not isinstance(x, (int, float))) or (x <= 0):
        raise ValueError('multiplier는 양수여야 합니다.')


def valid_check_date_unit(x: str) -> str:
    if isinstance(x, str):
        x = x.lower()
        valid_units = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
        if x in valid_units:
            return x
    raise ValueError(f'unit은 {", ".join(valid_units)} 중 하나여야 합니다.')


def valid_check_na_position(x: str) -> str:
    if isinstance(x, str):
        x = x.lower()
        valid_na_positions = ['first', 'last']
        if x in valid_na_positions:
            return x
    raise ValueError(f'na_position은 {", ".join(valid_na_positions)} 중 하나여야 합니다.')


def valid_check_string_case(x: str) -> str:
    if isinstance(x, str):
        x = x.lower()
        valid_string_cases = ['upper', 'lower', 'title', 'capitalize']
        if x in valid_string_cases:
            return x
    raise ValueError(f'case은 {", ".join(valid_string_cases)} 중 하나여야 합니다.')


def valid_check_categorize_unit(x: int) -> None:
    valid_units = [5, 10]
    if (not isinstance(x, int)) or (x not in valid_units):
        raise ValueError(f'unit은 {", ".join(map(str, valid_units))} 중 하나여야 합니다.')


def valid_check_categorize_method(x: str) -> str:
    if isinstance(x, str):
        x = x.lower()
        valid_methods = ['floor', 'mean', 'string']
        if x in valid_methods:
            return x
    raise ValueError(f'method은 {", ".join(valid_methods)} 중 하나여야 합니다.')


def valid_check_categorize_bins_length(bins_length: int) -> None:
    if (not isinstance(bins_length, int)) or (bins_length < 2):
        raise ValueError('구간 경계값 개수는 최소 2개 이상이어야 합니다.')


def valid_check_categorize_bins_order(bins: list) -> None:
    if (not isinstance(bins, list)) or (sorted(bins) != bins):
        raise ValueError('구간 경계값은 오름차순으로 정렬한 목록이어야 합니다.')


def valid_check_categorize_labels_length(labels: list, bins_length: int) -> None:
    if labels is None:
        return
    if (not isinstance(labels, list)) or (len(labels) != bins_length - 1):
        raise ValueError('레이블 목록은 구간 수보다 1개 적어야 합니다.')


def valid_check_random_seed(seed: Union[int, None]) -> None:
    # seed 검증
    if (seed is not None) and (not isinstance(seed, int)):
        # 타입 힌트 때문에 Code is unreachable 나오지만
        # 타입 힌트는 실행 시 영향이 없으므로 에러 처리 코드 있어야 함
        raise ValueError('seed는 정수여야 합니다.')


def valid_check_random_start(start: int) -> None:
    # start 검증
    if not isinstance(start, int):
        # 타입 힌트는 실행 시 영향이 없으므로 에러 처리 코드 있어야 함
        raise ValueError('시작값은 정수여야 합니다.')


def valid_check_std(v: Union[int, float]) -> None:
    if (not isinstance(v, (int, float))) or (v < 0):
        raise ValueError('std는 0 또는 양수여야 합니다.')


def valid_check_mean(v: Union[int, float]) -> None:
    if not isinstance(v, (int, float)):
        # 타입 힌트는 실행 시 영향이 없으므로 에러 처리 코드 있어야 함
        raise ValueError('평균값은 숫자여야 합니다.')


def valid_check_min_max(v: Union[int, float]) -> None:
    if not isinstance(v, (int, float)):
        # 타입 힌트는 실행 시 영향이 없으므로 에러 처리 코드 있어야 함
        raise ValueError('최소값 또는 최대값은 숫자여야 합니다.')


def valid_check_round_decimals(v: int) -> None:
    if not isinstance(v, int):
        # 타입 힌트는 실행 시 영향이 없으므로 에러 처리 코드 있어야 함
        raise ValueError('남길 자릿수는 정수여야 합니다.')


def valid_check_round_method(v: str) -> None:
    if isinstance(v, str):
        v = v.lower()
        valid_methods = ['round', 'floor', 'ceil']
        if v in valid_methods:
            return v
    raise ValueError(f'method는 {", ".join(valid_methods)} 중 하나여야 합니다.')


def valid_check_truncate_digits(v: int) -> None:
    if (not isinstance(v, int)) or (v <= 0):
        raise ValueError('digits는 양의 정수여야 합니다.')


def valid_check_bound(top: Any, bottom: Any) -> None:
    if (top is None) and (bottom is None):
        raise ValueError('top과 bottom 중 하나는 반드시 지정되어야 합니다.')
    if (isinstance(top, bool) and (not top)) and (isinstance(bottom, bool) and (not bottom)):
        raise ValueError('top과 bottom 중 하나는 반드시 True이어야 합니다.')


def valid_check_bound_value(v: Union[int, float, None]) -> None:
    if v is None:
        return
    if not isinstance(v, (int, float)):
        # 타입 힌트는 실행 시 영향이 없으므로 에러 처리 코드 있어야 함
        raise ValueError('경계값, 대체값은 숫자여야 합니다.')


def valid_check_threshold(v: Union[int, float, None]) -> None:
    if not isinstance(v, (int, float)):
        raise ValueError('threshold는 숫자여야 합니다.')


def valid_check_percentile_range_top(v: Union[int, float, None]) -> None:
    if v is None:
        return
    if (not isinstance(v, (int, float))) or (v < 50) or (v > 100):
        raise ValueError('백분위수는 50 - 100 사이 숫자여야 합니다.')


def valid_check_percentile_range_bottom(v: Union[int, float, None]) -> None:
    if v is None:
        return
    if (not isinstance(v, (int, float))) or (v < 0) or (v > 50):
        raise ValueError('백분위수는 0 - 50 사이 숫자여야 합니다.')


def valid_check_substring_start_end(v: Union[int, None]) -> None:
    if v is None:
        return
    if not isinstance(v, int):
        # 타입 힌트는 실행 시 영향이 없으므로 에러 처리 코드 있어야 함
        raise ValueError('시작값 또는 끝값은 정수여야 합니다.')
