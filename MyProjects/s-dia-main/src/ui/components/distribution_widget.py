import os
from PySide6.QtWidgets import QWidget, QMessageBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget, QFrame, QPushButton, QProgressBar
from PySide6.QtCore import Qt, QTimer, Signal, QThread
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.font_manager as fm
import logging
import platform
import random
from functools import lru_cache

class DataWorker(QThread):
    finished = Signal(object)
    progress = Signal(int)
    error = Signal(str)
    
    def __init__(self, df, column, chart_type, parent=None):
        super().__init__(parent)
        self.df = df
        self.column = column
        self.chart_type = chart_type
        self.sample_threshold = 10000  # 샘플링 임계값
        
    def run(self):
        try:
            series = self.df[self.column]
            
            # 대용량 데이터 샘플링
            if len(series) > self.sample_threshold:
                series = series.sample(n=self.sample_threshold, random_state=42)
            
            # 결측치 정보
            missing_info = {
                'count': series.isna().sum(),
                'total': len(series),
                'ratio': (series.isna().sum() / len(series)) * 100
            }
            
            # 데이터 타입 확인
            is_numeric = pd.api.types.is_numeric_dtype(series)
            
            # 차트 데이터 계산
            if self.chart_type == "히스토그램":
                if is_numeric:
                    q1, q3 = series.quantile([0.01, 0.99])
                    data = series[(series >= q1) & (series <= q3)]
                    chart_data = {'type': 'histogram', 'data': data}
                else:
                    # 문자형 데이터는 바 차트로 표시
                    value_counts = series.value_counts()
                    if len(value_counts) > 50:
                        value_counts = value_counts.head(50)
                    chart_data = {'type': 'bar', 'data': value_counts}
            
            elif self.chart_type == "박스플롯":
                if is_numeric:
                    chart_data = {'type': 'boxplot', 'data': series}
                else:
                    # 문자형 데이터는 바 차트로 표시
                    value_counts = series.value_counts()
                    if len(value_counts) > 50:
                        value_counts = value_counts.head(50)
                    chart_data = {'type': 'bar', 'data': value_counts}
            
            elif self.chart_type == "바 차트":
                value_counts = series.value_counts()
                if len(value_counts) > 50:
                    value_counts = value_counts.head(50)
                chart_data = {'type': 'bar', 'data': value_counts}
            
            self.finished.emit({'chart_data': chart_data, 'missing_info': missing_info})
            
        except Exception as e:
            self.error.emit(str(e))

class DistributionWidget(QWidget):
    def __init__(self, df: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # 데이터프레임은 참조만 저장 (복사하지 않음)
        self.df = df
        
        # 페이지네이션 관련 변수
        self.current_page = 1
        self.items_per_page = 50
        self.total_pages = 1
        
        # 현재 데이터 저장
        self.current_value_counts = None
        
        # 작업자 스레드
        self.worker = None
        
        # 디바운싱 타이머
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._delayed_update)
        
        # 한글 폰트 설정
        self.font_prop = self._setup_korean_font()
        
        # matplotlib 및 seaborn 설정
        self._setup_plot_style()
        
        # UI 설정
        self.setup_ui()
        
        # 컬럼 목록 설정
        self.setup_column_list()
        
        # 시그널 연결
        self._connect_signals()
        
        # 첫 번째 컬럼 선택
        if self.column_list.count() > 0:
            self.column_list.setCurrentRow(0)
    
    def _setup_plot_style(self):
        """플롯 스타일 설정"""
        plt.style.use('default')
        sns.set_style("whitegrid", {
            'axes.facecolor': 'white',
            'figure.facecolor': 'white',
            'grid.color': '#e9ecef',
            'text.color': 'black'
        })
        
        # Figure 설정 - DPI 최적화
        self.figure = Figure(facecolor='white', dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#f8f9fa')
        
        # 그리드 설정
        self.ax.grid(True, axis='y', linestyle='--', alpha=0.7, color='#dee2e6')
        
        # 호버 주석 초기화
        self.hover_annotation = None
    
    def setup_ui(self):
        """UI를 설정합니다."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 왼쪽 패널 (파란색 배경)
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #1864ab;
                border: none;
                border-radius: 4px;
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
            QListWidget {
                background-color: white;
                border: none;
                border-radius: 4px;
            }
            QComboBox {
                background-color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #dee2e6;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4dabf7;
                border-radius: 4px;
            }
        """)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        columns_label = QLabel("컬럼 목록")
        self.column_list = QListWidget()
        self.chart_type = QComboBox()
        self.chart_type.addItems(["히스토그램", "박스플롯", "바 차트"])
        
        left_layout.addWidget(columns_label)
        left_layout.addWidget(self.chart_type)
        left_layout.addWidget(self.column_list)
        
        # 오른쪽 패널 (차트)
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border: none;
            }
        """)
        
        # 플롯 영역
        self.plot_layout = QVBoxLayout(right_panel)
        self.plot_layout.setContentsMargins(10, 10, 10, 10)
        
        # 프로그레스 바 추가
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(2)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.plot_layout.addWidget(self.progress_bar)
        
        # 캔버스 추가
        self.plot_layout.addWidget(self.canvas)
        
        # 페이지네이션 컨트롤
        pagination_layout = QHBoxLayout()
        self.prev_button = QPushButton("이전")
        self.next_button = QPushButton("다음")
        self.page_label = QLabel("페이지: 1 / 1")
        self.page_label.setAlignment(Qt.AlignCenter)
        
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_button)
        
        # 페이지네이션 버튼 스타일
        pagination_style = """
            QPushButton {
                background-color: #1864ab;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #1971c2;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
            }
        """
        self.prev_button.setStyleSheet(pagination_style)
        self.next_button.setStyleSheet(pagination_style)
        
        # 플롯 레이아웃에 페이지네이션 추가
        self.plot_layout.addLayout(pagination_layout)
        
        # 메인 레이아웃에 패널 추가
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, stretch=1)
    
    def _setup_korean_font(self):
        """한글 폰트 설정"""
        try:
            if platform.system() == 'Windows':
                # Windows 한글 폰트 경로
                font_paths = [
                    'C:/Windows/Fonts/malgun.ttf',    # 맑은 고딕
                    'C:/Windows/Fonts/gulim.ttc',     # 굴림
                    'C:/Windows/Fonts/batang.ttc',    # 바탕
                    'C:/Windows/Fonts/NanumGothic.ttf',  # 나눔고딕
                ]
                
                # 사용 가능한 폰트 찾기
                font_path = None
                for path in font_paths:
                    if os.path.exists(path):
                        font_path = path
                        break
                
                if font_path:
                    # 폰트 추가 및 설정
                    font_prop = fm.FontProperties(fname=font_path)
                    plt.rcParams['font.family'] = font_prop.get_name()
                    plt.rcParams['font.sans-serif'] = [font_prop.get_name(), 'Malgun Gothic', 'NanumGothic']
                    plt.rcParams['axes.unicode_minus'] = False
                    return font_prop
                    
            # Windows가 아니거나 폰트를 찾지 못한 경우
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['font.sans-serif'] = ['Malgun Gothic', 'NanumGothic', 'Arial Unicode MS']
            plt.rcParams['axes.unicode_minus'] = False
            return None
                
        except Exception as e:
            self.logger.error(f"한글 폰트 설정 중 오류: {str(e)}")
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['font.sans-serif'] = ['Malgun Gothic', 'NanumGothic', 'Arial Unicode MS']
            plt.rcParams['axes.unicode_minus'] = False
            return None
    
    def setup_column_list(self):
        """컬럼 목록을 설정합니다."""
        try:
            for column in self.df.columns:
                self.column_list.addItem(str(column))
        except Exception as e:
            self._show_error("컬럼 목록 설정 오류", str(e))
    
    def previous_page(self):
        """이전 페이지로 이동"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_timer.start(300)
    
    def next_page(self):
        """다음 페이지로 이동"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_timer.start(300)
    
    def update_pagination_controls(self):
        """페이지네이션 컨트롤 상태 업데이트"""
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < self.total_pages)
        self.page_label.setText(f"페이지: {self.current_page} / {self.total_pages}")

    def _connect_signals(self):
        """시그널 연결"""
        self.prev_button.clicked.connect(self.previous_page)
        self.next_button.clicked.connect(self.next_page)
        self.column_list.currentItemChanged.connect(lambda: self.update_timer.start(300))  # 300ms 디바운싱
        self.chart_type.currentIndexChanged.connect(lambda: self.update_timer.start(300))
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)
    
    def _delayed_update(self):
        """디바운싱된 업데이트 함수"""
        current_item = self.column_list.currentItem()
        if not current_item:
            return
            
        column = current_item.text()
        chart_type = self.chart_type.currentText()
        
        # 이전 작업자가 있다면 중단
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        # 새 작업자 생성 및 시작
        self.worker = DataWorker(self.df, column, chart_type, self)
        self.worker.finished.connect(self._handle_worker_result)
        self.worker.error.connect(self._handle_worker_error)
        self.progress_bar.setVisible(True)
        self.worker.start()
    
    def _handle_worker_result(self, result):
        """작업자 결과 처리"""
        self.progress_bar.setVisible(False)
        chart_data = result['chart_data']
        missing_info = result['missing_info']
        
        try:
            # 이전 플롯 지우기
            self.ax.clear()
            
            # 차트 그리기
            if chart_data['type'] == 'histogram':
                self._plot_histogram(chart_data['data'])
            elif chart_data['type'] == 'boxplot':
                self._plot_boxplot(chart_data['data'])
            elif chart_data['type'] == 'bar':
                self._plot_bar(chart_data['data'])
            
            # 제목 설정
            column = self.column_list.currentItem().text()
            title = f"{column} 분포"
            if missing_info['count'] > 0:
                title += f"\n(결측치: {missing_info['count']:,}개, {missing_info['ratio']:.1f}%)"
            
            self._apply_plot_style(title)
            
            # 캔버스 업데이트
            self.figure.tight_layout()
            self.canvas.draw_idle()
            
        except Exception as e:
            self.logger.error(f"그래프 생성 오류: {str(e)}")
            self._show_error("그래프 생성 오류", str(e))
    
    def _handle_worker_error(self, error_message):
        """작업자 에러 처리"""
        self.progress_bar.setVisible(False)
        self._show_error("데이터 처리 오류", error_message)
    
    @lru_cache(maxsize=128)
    def generate_colors(self, n):
        """랜덤 파스텔 색상을 생성하고 캐시"""
        colors = []
        for _ in range(n):
            h = random.random()
            s = 0.3 + random.random() * 0.3
            v = 0.9 + random.random() * 0.1
            rgb = plt.cm.hsv(h)
            colors.append(rgb)
        return colors

    def _plot_histogram(self, series):
        """히스토그램을 그립니다."""
        if pd.api.types.is_numeric_dtype(series):
            sns.histplot(data=series, ax=self.ax, color='#4dabf7')
            self.ax.set_xlabel(series.name, color='black', fontsize=10)
            self.ax.set_ylabel('빈도', color='black', fontsize=10)
        else:
            # 문자형 데이터는 바 차트로 표시
            self._plot_bar(series.value_counts())
    
    def _plot_boxplot(self, series):
        """박스플롯을 그립니다."""
        if pd.api.types.is_numeric_dtype(series):
            sns.boxplot(y=series, ax=self.ax, color='#4dabf7')
            self.ax.set_ylabel(series.name, color='black', fontsize=10)
        else:
            # 문자형 데이터는 바 차트로 표시
            self._plot_bar(series.value_counts())
    
    def _plot_bar(self, value_counts):
        """바 차트를 그립니다."""
        # 데이터가 너무 많은 경우 상위 50개만 표시
        if len(value_counts) > 50:
            value_counts = value_counts.head(50)
        
        # 그래프 크기 설정
        fig_width = min(15, max(8, len(value_counts) * 0.2))
        fig_height = 6
        self.figure.set_size_inches(fig_width, fig_height)
        
        # 랜덤 색상 생성
        colors = self.generate_colors(len(value_counts))
        
        # 바 차트 그리기
        bars = self.ax.bar(range(len(value_counts)), value_counts.values, color=colors)
        
        # x축 레이블 설정
        if self.font_prop:
            self.ax.set_xticks(range(len(value_counts)))
            self.ax.set_xticklabels(value_counts.index, rotation=45, ha='right',
                                  fontsize=8, fontproperties=self.font_prop)
        else:
            self.ax.set_xticks(range(len(value_counts)))
            self.ax.set_xticklabels(value_counts.index, rotation=45, ha='right',
                                  fontsize=8)
        
        # y축 레이블 설정
        if self.font_prop:
            self.ax.set_ylabel('빈도', color='black', fontsize=10,
                             fontproperties=self.font_prop)
        else:
            self.ax.set_ylabel('빈도', color='black', fontsize=10)
        
        # 축 스타일 설정
        self.ax.tick_params(axis='x', colors='black', length=0)
        self.ax.tick_params(axis='y', colors='black')
        
        # 테두리 제거
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        
        # 그래프 여백 조정
        self.figure.tight_layout()
        
        # 레이아웃 조정
        self.ax.margins(x=0.01)
        self.ax.tick_params(axis='x', pad=5)
        self.figure.subplots_adjust(bottom=0.2)
        
        # 바 객체 저장 (호버 이벤트에서 사용)
        self.bars = bars
        self.value_counts = value_counts

    def on_hover(self, event):
        """마우스 호버 이벤트 처리"""
        if not hasattr(self, 'bars') or event.inaxes != self.ax:
            return
            
        # 이전 주석 제거
        if self.hover_annotation:
            self.hover_annotation.remove()
            self.hover_annotation = None
            
        for i, bar in enumerate(self.bars):
            if bar.contains(event)[0]:
                # 막대 위에 값 표시
                value = self.value_counts.iloc[i]
                category = self.value_counts.index[i]
                text = f'{category}\n{value:,}'
                
                # 주석 생성
                self.hover_annotation = self.ax.annotate(
                    text,
                    xy=(i, value),
                    xytext=(0, 10),
                    textcoords='offset points',
                    ha='center',
                    va='bottom',
                    bbox=dict(
                        boxstyle='round,pad=0.5',
                        fc='white',
                        ec='gray',
                        alpha=0.8
                    ),
                    fontproperties=self.font_prop if self.font_prop else None
                )
                self.canvas.draw_idle()
                break
        else:
            self.canvas.draw_idle()

    def _show_error(self, title, message):
        """에러 메시지를 표시합니다."""
        QMessageBox.critical(self, title, message)
        
    def _show_message(self, title, message):
        """정보 메시지를 표시합니다."""
        self.ax.clear()
        self.ax.text(0.5, 0.5, message,
                    ha='center', va='center',
                    color='black',
                    fontproperties=self.font_prop if self.font_prop else None,
                    transform=self.ax.transAxes)
        self.canvas.draw()

    def _apply_plot_style(self, title):
        """그래프 스타일을 적용합니다."""
        # 제목 설정
        if self.font_prop:
            self.ax.set_title(title, color='black', pad=20, fontsize=12, fontproperties=self.font_prop)
        else:
            self.ax.set_title(title, color='black', pad=20, fontsize=12)
        
        # 축 레이블 색상 및 크기 설정
        self.ax.tick_params(colors='black', labelsize=10)
        
        # 테두리 색상 설정
        for spine in self.ax.spines.values():
            spine.set_color('black')
        
        # x축 레이블이 있는 경우 회전 및 크기 조정
        if self.ax.get_xticklabels():
            if self.font_prop:
                self.ax.set_xticklabels(
                    self.ax.get_xticklabels(),
                    rotation=45,
                    ha='right',
                    fontsize=8,
                    fontproperties=self.font_prop
                )
            else:
                self.ax.set_xticklabels(
                    self.ax.get_xticklabels(),
                    rotation=45,
                    ha='right',
                    fontsize=8
                ) 