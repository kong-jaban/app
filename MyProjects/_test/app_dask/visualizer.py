import matplotlib.pyplot as plt

def plot_distribution(df, column, title):
    """
    데이터의 분포를 시각화하는 함수
    :param df: Dask DataFrame
    :param column: 시각화할 컬럼명
    :param title: 그래프 제목
    """
    if column in df.columns:
        data = df[column].dropna().compute()
        plt.figure(figsize=(8, 5))
        plt.hist(data, bins=20, alpha=0.7, color='blue', edgecolor='black')
        plt.title(title)
        plt.xlabel(column)
        plt.ylabel("Count")
        plt.show()