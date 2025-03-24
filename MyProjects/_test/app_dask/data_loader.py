# data_loader.py
import dask.dataframe as dd

def load_csv(file_path):
    df = dd.read_csv(file_path, assume_missing=True)
    return df

# anonymizer.py
def anonymize_data(df, drop_columns=None, bin_columns=None, bin_sizes=None):
    if drop_columns:
        df = df.drop(columns=drop_columns, errors='ignore')
    if bin_columns and bin_sizes:
        for col in bin_columns:
            if col in df.columns:
                df[col] = dd.cut(df[col], bins=bin_sizes.get(col, 5), labels=False)
    return df
