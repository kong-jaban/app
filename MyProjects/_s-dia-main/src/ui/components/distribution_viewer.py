from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QHBoxLayout, QPushButton, QLabel, QTabWidget, QTableWidget, QTableWidgetItem, QFileDialog, QLineEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from PySide6.QtCore import Qt
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform

class DistributionViewer(QWidget):
    def __init__(self, df: pd.DataFrame, project_name=None):
        super().__init__()
        self.df = df
        self.project_name = project_name or "프로젝트"
        self.distribution_data = self._precompute_distributions()
        self.current_page = 0
        self.items_per_page = 20
        self.current_column = None  # 현재 선택된 컬럼 저장
        self.current_chart_type = None  # 현재 선택된 차트 타입 저장
        self.sort_column = 0  # 0: 값, 1: 카운트
        self.sort_order = Qt.AscendingOrder
        self._last_tooltip = None  # 툴팁 중복 방지용
        self._init_ui()
        self._setup_font()

    def _setup_font(self):
        # 운영체제별 기본 한글 폰트 설정
        if platform.system() == 'Windows':
            font_path = 'C:/Windows/Fonts/malgun.ttf'  # 맑은 고딕
        elif platform.system() == 'Darwin':  # macOS
            font_path = '/System/Library/Fonts/AppleSDGothicNeo.ttc'
        else:  # Linux
            font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'

        # 폰트 설정
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
        plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 탭 위젯 추가
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # 차트 탭
        self.chart_widget = QWidget()
        chart_layout = QVBoxLayout(self.chart_widget)
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("이전")
        self.next_button = QPushButton("다음")
        self.page_label = QLabel("1/1")
        # 페이지 번호 입력 및 이동 버튼
        self.page_input = QLineEdit()
        self.page_input.setFixedWidth(40)
        self.page_input.setPlaceholderText("페이지")
        self.goto_button = QPushButton("이동")
        self.goto_button.setFixedWidth(40)
        self.goto_button.clicked.connect(self.goto_page)
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.page_label)
        nav_layout.addWidget(self.page_input)
        nav_layout.addWidget(self.goto_button)
        nav_layout.addWidget(self.next_button)
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)
        chart_layout.addLayout(nav_layout)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.tab_widget.addTab(self.chart_widget, "차트")

        # 테이블 탭
        self.table_widget = QWidget()
        table_layout = QVBoxLayout(self.table_widget)
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["값", "카운트"])
        self.table.horizontalHeader().sectionClicked.connect(self.on_table_header_clicked)
        table_layout.addWidget(self.table)
        # CSV 다운로드 버튼
        csv_layout = QHBoxLayout()
        csv_layout.addStretch()
        self.csv_button = QPushButton("CSV 다운로드")
        self.csv_button.setStyleSheet('''
            QPushButton {
                background-color: #1976d2;
                color: white;
                border-radius: 5px;
                padding: 6px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        ''')
        self.csv_button.clicked.connect(self.download_csv)
        csv_layout.addWidget(self.csv_button)
        table_layout.addLayout(csv_layout)
        self.tab_widget.addTab(self.table_widget, "테이블")

        self.setLayout(layout)

    def _precompute_distributions(self):
        dist = {}
        for col in self.df.columns:
            # 모든 컬럼에 대해 value_counts() 사용
            dist[col] = self.df[col].value_counts()
        return dist

    def display_distribution(self, col, chart_type=None):
        if not col:
            return
        # 컬럼이 바뀌면 디폴트로 초기화
        if col != self.current_column:
            self.current_page = 0
            self.sort_column = 0
            self.sort_order = Qt.AscendingOrder
        self.current_column = col
        if chart_type is not None:
            self.current_chart_type = chart_type
        # 차트 탭 업데이트
        self.update_chart()
        # 테이블 탭 업데이트
        self.update_table()

    def update_chart(self):
        if not self.current_column or self.current_column not in self.df.columns:
            return
        data = self.distribution_data[self.current_column]
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            if self.current_chart_type == "막대그래프":
                start_idx = self.current_page * self.items_per_page
                end_idx = start_idx + self.items_per_page
                page_data = data.iloc[start_idx:end_idx]
                ax.bar(range(len(page_data)), page_data.values, color="#6699cc")
                ax.set_xticks(range(len(page_data)))
                ax.set_xticklabels(page_data.index, rotation=45, ha='right')
            elif self.current_chart_type == "파이차트":
                start_idx = self.current_page * self.items_per_page
                end_idx = start_idx + self.items_per_page
                page_data = data.iloc[start_idx:end_idx]
                ax.pie(page_data.values, labels=page_data.index, autopct='%1.1f%%')
            else:
                ax.text(0.5, 0.5, '시각화할 수 없습니다.', ha='center')
            total_count = len(self.df[self.current_column])
            unique_count = len(data)
            ax.set_title(f"{self.current_column} - {self.current_chart_type}\n전체: {total_count:,}개, 고유값: {unique_count:,}개")
            total_pages = (len(data) + self.items_per_page - 1) // self.items_per_page
            self.page_label.setText(f"{self.current_page + 1}/{total_pages}")
            self.prev_button.setEnabled(self.current_page > 0)
            self.next_button.setEnabled(self.current_page < total_pages - 1)
            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            print(f"Error in update_chart: {str(e)}")
            ax.text(0.5, 0.5, f'오류 발생: {str(e)}', ha='center')
            self.canvas.draw()

    def update_table(self):
        if not self.current_column or self.current_column not in self.df.columns:
            return
        data = self.distribution_data[self.current_column]
        # 정렬
        if self.sort_column == 0:
            sorted_data = data.sort_index(ascending=(self.sort_order == Qt.AscendingOrder))
        else:
            sorted_data = data.sort_values(ascending=(self.sort_order == Qt.AscendingOrder))
        self.table.setRowCount(len(sorted_data))
        for i, (val, cnt) in enumerate(sorted_data.items()):
            self.table.setItem(i, 0, QTableWidgetItem(str(val)))
            self.table.setItem(i, 1, QTableWidgetItem(str(cnt)))
        # 헤더에 정렬 표시
        for col in range(2):
            order = self.table.horizontalHeader().sortIndicatorOrder() if col == self.sort_column else None
            self.table.horizontalHeaderItem(col).setText(("▲ " if col == self.sort_column and self.sort_order == Qt.AscendingOrder else ("▼ " if col == self.sort_column else "")) + ("값" if col == 0 else "카운트"))

    def on_table_header_clicked(self, logicalIndex):
        if self.sort_column == logicalIndex:
            self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            self.sort_column = logicalIndex
            self.sort_order = Qt.AscendingOrder
        self.update_table()

    def download_csv(self):
        if not self.current_column or self.current_column not in self.df.columns:
            return
        data = self.distribution_data[self.current_column]
        # 정렬
        if self.sort_column == 0:
            sorted_data = data.sort_index(ascending=(self.sort_order == Qt.AscendingOrder))
            sort_name = "asc" if self.sort_order == Qt.AscendingOrder else "desc"
        else:
            sorted_data = data.sort_values(ascending=(self.sort_order == Qt.AscendingOrder))
            sort_name = "asc" if self.sort_order == Qt.AscendingOrder else "desc"
        # DataFrame으로 변환 (값, 카운트)
        df_to_save = sorted_data.reset_index()
        df_to_save.columns = [self.current_column, "카운트"]
        # 파일명
        filename = f"분포_원본_{self.project_name}_{self.current_column}_{sort_name}.csv"
        path, _ = QFileDialog.getSaveFileName(self, "CSV로 저장", filename, "CSV Files (*.csv)")
        if path:
            df_to_save.to_csv(path, index=False, encoding="utf-8-sig")

    def on_mouse_move(self, event):
        if not self.current_column or self.current_column not in self.df.columns:
            self.canvas.setToolTip("")
            return
        data = self.distribution_data[self.current_column]
        # 현재 페이지 데이터
        start_idx = self.current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_data = data.iloc[start_idx:end_idx]
        if event.inaxes:
            if self.current_chart_type == "막대그래프":
                for i, rect in enumerate(event.inaxes.patches):
                    if rect.contains(event)[0]:
                        value = str(page_data.index[i])
                        count = str(page_data.values[i])
                        tip = f"값: {value}\n카운트: {count}"
                        if self._last_tooltip != tip:
                            self.canvas.setToolTip(tip)
                            self._last_tooltip = tip
                        return
                self.canvas.setToolTip("")
                self._last_tooltip = None
            elif self.current_chart_type == "파이차트":
                for i, wedge in enumerate(event.inaxes.patches):
                    if wedge.contains(event)[0]:
                        value = str(page_data.index[i])
                        count = str(page_data.values[i])
                        tip = f"값: {value}\n카운트: {count}"
                        if self._last_tooltip != tip:
                            self.canvas.setToolTip(tip)
                            self._last_tooltip = tip
                        return
                self.canvas.setToolTip("")
                self._last_tooltip = None
        else:
            self.canvas.setToolTip("")
            self._last_tooltip = None

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.display_distribution(self.current_column, self.current_chart_type)

    def next_page(self):
        data = self.distribution_data[self.current_column]
        total_pages = (len(data) + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.display_distribution(self.current_column, self.current_chart_type)

    def goto_page(self):
        if not self.current_column or self.current_column not in self.df.columns:
            return
        data = self.distribution_data[self.current_column]
        total_pages = (len(data) + self.items_per_page - 1) // self.items_per_page
        try:
            page = int(self.page_input.text())
            if 1 <= page <= total_pages:
                self.current_page = page - 1
                self.update_chart()
            else:
                self.page_input.setText("")
        except ValueError:
            self.page_input.setText("")

    def closeEvent(self, event):
        try:
            if hasattr(self, 'figure'):
                self.figure.clear()
            if hasattr(self, 'canvas'):
                self.canvas.close()
        except Exception as e:
            print(f"Error in closeEvent: {str(e)}")
        finally:
            super().closeEvent(event)

    def __del__(self):
        try:
            if hasattr(self, 'figure'):
                self.figure.clear()
            if hasattr(self, 'canvas'):
                self.canvas.close()
        except Exception as e:
            print(f"Error in __del__: {str(e)}") 