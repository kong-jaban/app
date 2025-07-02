import logging
import os
from dask.dataframe import read_csv, read_parquet
import pandas as pd

from ui.project_schema import Schema

logger = logging.getLogger(__name__)  

def get_schema(df):
    """스키마 정보 가져오기"""
    dtypes = df.dtypes
    
    # 컬럼명과 데이터 타입 출력
    schrmas = []
    for column_name, data_type in dtypes.items():
        # row = [column, dtype]
        schema = Schema()
        schema.name = column_name
        schema.data_type = data_type
        schrmas.append(schema)
    
    return schrmas

def read_file(file_path, is_csv, header_line, charset, separator, read_first_line=0):
    try:
        if os.path.exists(file_path):
            # dask를 사용하여 CSV 파일 읽기
            if is_csv:
                # 먼저 pandas로 샘플을 읽어서 데이터 타입 추론
                sample_df = pd.read_csv(file_path, 
                                        encoding=charset,
                                        sep=separator,
                                        header=header_line,
                                        nrows=1000,  # 충분한 샘플로 타입 추론
                                        encoding_errors='replace')
                
                # 추론된 데이터 타입을 dask에 적용
                dtype_dict = sample_df.dtypes.to_dict()
                
                # dask로 전체 파일 읽기
                df = read_csv(file_path, 
                            encoding=charset,
                            sep=separator,
                            header=header_line,
                            dtype=dtype_dict,
                            encoding_errors='replace')
            else: # file_path.lower().endswith('.parquet'):
                df = read_parquet(file_path)

            file_schemas = get_schema(df)
            if read_first_line > 0:
                first_rows = df.head(read_first_line)
            else:
                first_rows = []
            return file_schemas, first_rows
        else:
            raise ValueError(f"선택한 데이타가 존재하지 않습니다. : {file_path}")
    except Exception as e:
        # 오류 메시지에서 문제 정보 추출
        error_msg = str(e)
        logger.error(f"CSV 읽기 오류: {error_msg}")
        
        # dask 오류 메시지에서 컬럼 정보 추출
        if "Mismatched dtypes found" in error_msg:
            err_coulmns = []
            #
            # 오류 메시지에서 컬럼 정보 파싱
            lines = error_msg.split('\n')
            for line in lines:
                if '|' in line and 'Column' not in line and 'Found' not in line and 'Expected' not in line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        col_name = parts[1].strip()
                        found_type = parts[2].strip()
                        expected_type = parts[3].strip()
                        if col_name and found_type != expected_type:
                            err_coulmns.append(f"{col_name}: {found_type} → {expected_type}")
            raise ValueError(f"\n데이터 타입에 문제가 있습니다. {", ".join(err_coulmns)}")
        
        # invalid literal 오류 처리
        elif "invalid literal for int()" in error_msg or "invalid literal for float()" in error_msg:
            # print("\n숫자 변환 오류:")
            # 오류 메시지에서 값 추출
            if "invalid literal for int() with base 10:" in error_msg:
                value = error_msg.split("invalid literal for int() with base 10:")[1].strip().strip("'")
                print(f"  정수 변환 실패: 값 '{value}'이 숫자가 아닙니다")
                raise ValueError(f"\n{value} 컬럼에 잘못된 값이 있어서 읽을 수 없습니다.")
                print(f"  정수 변환 실패: 값 '{value}'이 숫자가 아닙니다")
            elif "invalid literal for float():" in error_msg:
                value = error_msg.split("invalid literal for float():")[1].strip().strip("'")
                raise ValueError(f"\n{value} 컬럼에 잘못된 값이 있어서 읽을 수 없습니다.")
        
        # could not convert string to float 오류 처리
        elif "could not convert string to float:" in error_msg:
            # print("\n문자열을 실수로 변환 오류:")
            value = error_msg.split("could not convert string to float:")[1].strip().strip("'")
            raise ValueError(f"\n{value} 컬럼에 잘못된 값이 있어서 읽을 수 없습니다.")
        
        # 기타 변환 오류들
        elif "ValueError" in error_msg and "convert" in error_msg.lower():
            # print("\n데이터 타입 변환 오류:")
            raise ValueError(f"\n잘못된 값이 있어서 읽을 수 없습니다.")
        
        # 컬럼별 상세 오류 정보가 있는 경우
        elif "The following columns also raised exceptions on conversion:" in error_msg:
            raise ValueError(f"\n잘못된 값이 있어서 읽을 수 없습니다.")
        else:
            raise e
            