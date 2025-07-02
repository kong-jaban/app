import matplotlib
matplotlib.use("Agg")  # GUI 백엔드 대신 'Agg' 사용
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
    else:
        msg = QMessageBox()
        msg.setWindowTitle("오류")
        msg.setText(f"'{column}' 컬럼이 존재하지 않습니다.")
        msg.exec()
