import matplotlib.pyplot as plt

def plot_distribution(df, column, title):
    if column in df.columns:
        data = df[column].dropna().compute()
        plt.figure(figsize=(8, 5))
        plt.hist(data, bins=20, alpha=0.7, color='blue', edgecolor='black')
        plt.title(title)
        plt.xlabel(column)
        plt.ylabel("Count")
        plt.show()