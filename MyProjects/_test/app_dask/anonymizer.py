def anonymize_data(df, drop_columns=None, bin_columns=None, bin_sizes=None):
    """
    컬럼 삭제 및 범주화 기능을 포함한 비식별 처리
    :param df: Dask DataFrame
    :param drop_columns: 삭제할 컬럼 리스트
    :param bin_columns: 범주화할 컬럼 리스트
    :param bin_sizes: 각 컬럼별 구간 개수 딕셔너리
    :return: 변환된 Dask DataFrame
    """
    if drop_columns:
        df = df.drop(columns=drop_columns, errors='ignore')
    if bin_columns and bin_sizes:
        for col in bin_columns:
            if col in df.columns:
                df[col] = dd.cut(df[col], bins=bin_sizes.get(col, 5), labels=False)
    return df