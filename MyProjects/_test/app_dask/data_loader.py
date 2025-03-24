import dask.dataframe as dd

def load_csv(file_path, sample_size=5):
    """
    대용량 CSV 파일을 Dask DataFrame으로 로드하고 일부 샘플을 출력
    :param file_path: CSV 파일 경로
    :param sample_size: 출력할 샘플 크기
    :return: Dask DataFrame
    """
    print("CSV 파일 로드 중...")
    df = dd.read_csv(file_path, assume_missing=True)
    print("데이터 샘플:")
    print(df.head(sample_size))  # 일부 데이터 출력
    return df