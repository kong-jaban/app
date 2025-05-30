import dask.dataframe as dd

def load_csv(file_path):
    df = dd.read_csv(file_path, assume_missing=True)
    return df.compute()  # CSV 불러올 때 Pandas DataFrame으로 변환

def save_csv(df, file_path):
    df.compute().to_csv(file_path, index=False)
