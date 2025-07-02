import hashlib
import base64
from typing import Literal, Union
import dask.dataframe as dd
from ups.dask.valid_check import (
    str_to_list,
    valid_check_blake2b_length,
    valid_check_blake2s_length,
    valid_check_blake_algorithm,
    valid_check_column_count,
    valid_check_column_exists,
    valid_check_encoding,
    valid_check_salt_position,
    valid_check_sha_algorithm,
    valid_check_sha_length,
    valid_check_shake_algorithm,
    valid_check_shake_length,
)


def _add_salt(value, salt, salt_position='suffix') -> str:
    if not salt:  # salt가 None이거나 빈 문자열인 경우
        return value

    valid_check_salt_position(salt_position)

    if salt_position == 'prefix':
        return f"{salt}{value}"
    elif salt_position == 'suffix':
        return f"{value}{salt}"


def _encode(hash_bytes, encoding='hex') -> str:
    encoding = valid_check_encoding(encoding)

    if encoding == 'base64':
        return base64.b64encode(hash_bytes).decode()

    s = hash_bytes.hex()
    return s.upper() if encoding == 'hex_upper' else s


def sha2(
    df: dd.DataFrame,
    columns: Union[str, list],
    length: Literal[224, 256, 384, 512] = 256,
    encoding: Literal['hex', 'hex_lower', 'hex_upper', 'base64'] = 'hex',
    salt: str = None,
    salt_position: Literal['prefix', 'suffix'] = 'suffix',
    output_columns: Union[str, list] = None,
) -> dd.DataFrame:
    """
    SHA-2 해시 함수를 사용하여 컬럼 값을 암호화하는 함수
    """
    return sha(
        df,
        columns,
        algorithm='sha2',
        length=length,
        encoding=encoding,
        salt=salt,
        salt_position=salt_position,
        output_columns=output_columns,
    )


def sha3(
    df: dd.DataFrame,
    columns: Union[str, list],
    length: Literal[224, 256, 384, 512] = 256,
    encoding: Literal['hex', 'hex_lower', 'hex_upper', 'base64'] = 'hex',
    salt: str = None,
    salt_position: Literal['prefix', 'suffix'] = 'suffix',
    output_columns: Union[str, list] = None,
) -> dd.DataFrame:
    """
    SHA-3 해시 함수를 사용하여 컬럼 값을 암호화하는 함수
    """
    return sha(
        df,
        columns,
        algorithm='sha3',
        length=length,
        encoding=encoding,
        salt=salt,
        salt_position=salt_position,
        output_columns=output_columns,
    )


def sha(
    df: dd.DataFrame,
    columns: Union[str, list],
    algorithm: Literal['sha2', 'sha3'] = 'sha2',
    length: Literal[224, 256, 384, 512] = 256,
    encoding: Literal['hex', 'hex_lower', 'hex_upper', 'base64'] = 'hex',
    salt: str = None,
    salt_position: Literal['prefix', 'suffix'] = 'suffix',
    output_columns: Union[str, list] = None,
) -> dd.DataFrame:
    """
    SHA-2/SHA-3 해시 함수를 사용하여 컬럼 값을 암호화하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : str or list
        처리할 컬럼 이름 또는 이름들의 리스트
    algorithm : str, default='sha256'
        SHA 알고리즘
        - SHA-2:
            - 'sha224': SHA-224 (224비트)
            - 'sha256': SHA-256 (256비트)
            - 'sha384': SHA-384 (384비트)
            - 'sha512': SHA-512 (512비트)
        - SHA-3:
            - 'sha3_224': SHA3-224 (224비트)
            - 'sha3_256': SHA3-256 (256비트)
            - 'sha3_384': SHA3-384 (384비트)
            - 'sha3_512': SHA3-512 (512비트)
    encoding : str, default='hex'
        결과 인코딩 방식
        - 'hex': 16진수 문자열
        - 'base64': Base64 문자열
    salt : str, default=None
        해시에 추가할 salt 값
        None이면 salt를 사용하지 않음
    salt_position : str, default='suffix'
        salt 추가 위치
        - 'prefix': 값 앞에 추가
        - 'suffix': 값 뒤에 추가
    output_columns : str or list, default=None
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
        None일 경우 원본 컬럼을 덮어씀

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame

    Examples:
    --------
    # SHA-256 해시
    df = sha(df, 'password',
             algorithm='sha256',
             salt='my_secret',
             output_columns='hashed_password')

    # SHA3-256 해시 (Base64 인코딩)
    df = sha(df, ['col1', 'col2'],
             algorithm='sha3_256',
             encoding='base64',
             salt='another_salt',
             salt_position='prefix')
    """
    columns = str_to_list(columns)
    valid_check_column_exists(df, columns)
    output_columns = columns if output_columns is None else str_to_list(output_columns)
    valid_check_column_count(columns, output_columns)
    valid_check_sha_length(length)
    algorithm = valid_check_sha_algorithm(algorithm)
    algorithm = f'sha3_{length}' if algorithm == 'sha3' else f'sha{length}'

    # 해시 함수 선택
    hash_func = getattr(hashlib, algorithm)

    def hash_value(x):
        salted_value = _add_salt(str(x), salt, salt_position)
        hash_bytes = hash_func(salted_value.encode()).digest()
        return _encode(hash_bytes, encoding)

    # 각 컬럼에 대해 처리 수행
    for col, out_col in zip(columns, output_columns):
        df[out_col] = df[col].map_partitions(lambda x: x.map(hash_value), meta=('out_col', 'object'))
        # df[out_col] = df[col].map(hash_value, meta=('out_col', 'object'))

    return df


def shake_128(
    df: dd.DataFrame,
    columns: Union[str, list],
    length: int = 32,
    encoding: Literal['hex', 'hex_lower', 'hex_upper', 'base64'] = 'hex',
    salt: str = None,
    salt_position: Literal['prefix', 'suffix'] = 'suffix',
    output_columns: Union[str, list] = None,
) -> dd.DataFrame:
    """
    SHAKE-128 해시 함수를 사용하여 컬럼 값을 암호화하는 함수
    """
    return shake(
        df,
        columns,
        algorithm='shake_128',
        length=length,
        encoding=encoding,
        salt=salt,
        salt_position=salt_position,
        output_columns=output_columns,
    )


def shake_256(
    df: dd.DataFrame,
    columns: Union[str, list],
    length: int = 16,
    encoding: Literal['hex', 'hex_lower', 'hex_upper', 'base64'] = 'hex',
    salt: str = None,
    salt_position: Literal['prefix', 'suffix'] = 'suffix',
    output_columns: Union[str, list] = None,
) -> dd.DataFrame:
    """
    SHAKE-256 해시 함수를 사용하여 컬럼 값을 암호화하는 함수
    """
    return shake(
        df,
        columns,
        algorithm='shake_256',
        length=length,
        encoding=encoding,
        salt=salt,
        salt_position=salt_position,
        output_columns=output_columns,
    )


def shake(
    df: dd.DataFrame,
    columns: Union[str, list],
    algorithm: Literal['shake_128', 'shake_256'] = 'shake_128',
    length: int = 16,
    encoding: Literal['hex', 'hex_lower', 'hex_upper', 'base64'] = 'hex',
    salt: str = None,
    salt_position: Literal['prefix', 'suffix'] = 'suffix',
    output_columns: Union[str, list] = None,
) -> dd.DataFrame:
    """
    SHAKE 해시 함수를 사용하여 컬럼 값을 암호화하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : str or list
        처리할 컬럼 이름 또는 이름들의 리스트
    algorithm : str, default='shake_128'
        SHAKE 알고리즘
        - 'shake_128': SHAKE128
        - 'shake_256': SHAKE256
    length : int, default=32
        출력 길이 (바이트)
    encoding : str, default='hex'
        결과 인코딩 방식
        - 'hex': 16진수 문자열
        - 'base64': Base64 문자열
    salt : str, default=None
        해시에 추가할 salt 값
        None이면 salt를 사용하지 않음
    salt_position : str, default='suffix'
        salt 추가 위치
        - 'prefix': 값 앞에 추가
        - 'suffix': 값 뒤에 추가
    output_columns : str or list, default=None
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
        None일 경우 원본 컬럼을 덮어씀

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame
    """
    columns = str_to_list(columns)
    # output_columns이 None이면 원본 컬럼명 사용
    output_columns = columns if output_columns is None else str_to_list(output_columns)

    valid_check_column_count(columns, output_columns)
    valid_check_column_exists(df, columns)
    valid_check_shake_length(length)
    algorithm = valid_check_shake_algorithm(algorithm)

    # 해시 함수 선택
    hash_func = getattr(hashlib, algorithm)

    def hash_value(x):
        salted_value = _add_salt(str(x), salt, salt_position)
        hash_bytes = hash_func(salted_value.encode()).digest(length)
        return _encode(hash_bytes, encoding)

    # 각 컬럼에 대해 처리 수행
    for col, out_col in zip(columns, output_columns):
        df[out_col] = df[col].map_partitions(lambda x: x.map(hash_value), meta=('out_col', 'object'))

    return df


def blake2b(
    df: dd.DataFrame,
    columns: Union[str, list],
    length: int = 16,
    encoding: Literal['hex', 'hex_lower', 'hex_upper', 'base64'] = 'hex',
    salt: str = None,
    salt_position: Literal['prefix', 'suffix'] = 'suffix',
    output_columns: Union[str, list] = None,
) -> dd.DataFrame:
    return blake(
        df,
        columns,
        algorithm='blake2b',
        length=length,
        encoding=encoding,
        salt=salt,
        salt_position=salt_position,
        output_columns=output_columns,
    )


def blake2s(
    df: dd.DataFrame,
    columns: Union[str, list],
    length: int = 16,
    encoding: Literal['hex', 'hex_lower', 'hex_upper', 'base64'] = 'hex',
    salt: str = None,
    salt_position: Literal['prefix', 'suffix'] = 'suffix',
    output_columns: Union[str, list] = None,
) -> dd.DataFrame:
    return blake(
        df,
        columns,
        algorithm='blake2s',
        length=length,
        encoding=encoding,
        salt=salt,
        salt_position=salt_position,
        output_columns=output_columns,
    )


def blake(
    df: dd.DataFrame,
    columns: Union[str, list],
    algorithm: Literal['blake2b', 'blake2s'] = 'blake2b',
    length: int = 64,
    encoding: Literal['hex', 'hex_lower', 'hex_upper', 'base64'] = 'hex',
    salt: str = None,
    salt_position: Literal['prefix', 'suffix'] = 'suffix',
    output_columns: Union[str, list] = None,
) -> dd.DataFrame:
    """
    BLAKE 해시 함수를 사용하여 컬럼 값을 암호화하는 함수

    Parameters:
    -----------
    df : dask.dataframe.DataFrame
        처리할 Dask DataFrame
    columns : str or list
        처리할 컬럼 이름 또는 이름들의 리스트
    algorithm : str, default='blake2b'
        BLAKE 알고리즘
        - 'blake2b': BLAKE2b (최대 64바이트)
        - 'blake2s': BLAKE2s (최대 32바이트)
    length : int, default=64
        출력 길이 (바이트)
        - blake2b: 1-64
        - blake2s: 1-32
    encoding : str, default='hex'
        결과 인코딩 방식
        - 'hex': 16진수 문자열
        - 'base64': Base64 문자열
    salt : str, default=None
        해시에 추가할 salt 값
        None이면 salt를 사용하지 않음
    salt_position : str, default='suffix'
        salt 추가 위치
        - 'prefix': 값 앞에 추가
        - 'suffix': 값 뒤에 추가
    output_columns : str or list, default=None
        결과를 저장할 새 컬럼 이름 또는 이름들의 리스트
        None일 경우 원본 컬럼을 덮어씀

    Returns:
    --------
    dask.dataframe.DataFrame
        처리된 DataFrame
    """
    columns = str_to_list(columns)
    output_columns = columns if output_columns is None else str_to_list(output_columns)

    valid_check_column_count(columns, output_columns)
    valid_check_column_exists(df, columns)

    algorithm = valid_check_blake_algorithm(algorithm)
    if algorithm == 'blake2b':
        valid_check_blake2b_length(length)
    elif algorithm == 'blake2s':
        valid_check_blake2s_length(length)

    # 해시 함수 선택
    hash_func = getattr(hashlib, algorithm)

    def hash_value(x):
        salted_value = _add_salt(str(x), salt, salt_position)
        hash_bytes = hash_func(salted_value.encode(), digest_size=length).digest()
        return _encode(hash_bytes, encoding)

    # 각 컬럼에 대해 처리 수행
    for col, out_col in zip(columns, output_columns):
        df[out_col] = df[col].map_partitions(lambda x: x.map(hash_value), meta=('out_col', 'object'))

    return df


# def tuple_hash(
#     df,
#     columns,
#     algorithm="sha256",
#     separator="|",
#     encoding="hex",
#     salt=None,
#     salt_position="prefix",
#     output_column=None,
# ):
#     """
#     여러 컬럼을 결합하여 하나의 해시값을 생성하는 함수

#     Parameters:
#     -----------
#     df : dask.dataframe.DataFrame
#         처리할 Dask DataFrame
#     columns : str or list
#         처리할 컬럼 이름 또는 이름들의 리스트
#     algorithm : str, default='sha256'
#         SHA-2 알고리즘
#         - 'sha224': SHA-224 (224비트)
#         - 'sha256': SHA-256 (256비트)
#         - 'sha384': SHA-384 (384비트)
#         - 'sha512': SHA-512 (512비트)
#     separator : str, default='|'
#         컬럼을 결합할 구분자
#     encoding : str, default='hex'
#         결과 인코딩 방식
#         - 'hex': 16진수 문자열
#         - 'base64': Base64 문자열
#     salt : str, default=None
#         해시에 추가할 salt 값
#         None이면 salt를 사용하지 않음
#     salt_position : str, default='prefix'
#         salt 추가 위치
#         - 'prefix': 결합된 값 앞에 추가
#         - 'suffix': 결합된 값 뒤에 추가
#     output_column : str, default=None
#         결과를 저장할 새 컬럼 이름
#         None일 경우 원본 컬럼을 덮어씀

#     Returns:
#     --------
#     dask.dataframe.DataFrame
#         처리된 DataFrame
#     """
#     columns = str_to_list(columns)
#     output_column = str_to_list(output_column)

#     # output_column이 None이면 원본 컬럼명 사용
#     output_column = output_column or columns

#     valid_check_column_count(columns, output_column)
#     valid_check_column_existence(df, columns)

#     valid_check_algorithm(algorithm)

#     # 알고리즘 검증
#     valid_algorithms = ["sha224", "sha256", "sha384", "sha512"]
#     if algorithm not in valid_algorithms:
#         raise ValueError(
#             f"algorithm은 {', '.join(valid_algorithms)} 중 하나여야 합니다."
#         )

#     # 인코딩 검증
#     if encoding not in ["hex", "base64"]:
#         raise ValueError("encoding은 'hex' 또는 'base64'여야 합니다.")

#     # salt_position 검증
#     if salt_position not in ["prefix", "suffix"]:
#         raise ValueError("salt_position은 'prefix' 또는 'suffix'여야 합니다.")

#     # 해시 함수 선택
#     hash_func = getattr(hashlib, algorithm)

#     def combine_hash(row):
#         # NA 값은 빈 문자열로 처리
#         values = [str(row[col]) if pd.notna(row[col]) else "" for col in columns]
#         # 구분자로 결합
#         combined = separator.join(values)
#         # salt 추가
#         salted_value = _add_salt(combined, salt, salt_position)

#         # 해시값 생성
#         if algorithm.startswith("shake"):
#             hash_bytes = getattr(hashlib, algorithm)(salted_value.encode()).digest(
#                 32
#             )
#         elif algorithm.startswith("blake2"):
#             hash_bytes = getattr(hashlib, algorithm)(
#                 salted_value.encode(), digest_size=32
#             ).digest()
#         else:
#             hash_bytes = getattr(hashlib, algorithm)(salted_value.encode()).digest()

#         return _encode(hash_bytes, encoding)

#     # 각 컬럼에 대해 처리 수행
#     for col, out_col in zip(columns, output_column):
#         df[out_col] = df.apply(combine_hash, axis=1, meta=('output', 'object'))

#     return df
