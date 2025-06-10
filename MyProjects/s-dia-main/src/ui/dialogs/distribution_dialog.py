import os
from PySide6.QtWidgets import QDialog, QMessageBox, QVBoxLayout
from PySide6.QtCore import Qt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.font_manager as fm
import logging
from ui.dialogs.Distribution_ui import Ui_DistributionDialog
import platform

class DistributionDialog(QDialog):
    def __init__(self, df: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.ui = Ui_DistributionDialog()
        self.ui.setupUi(self)
        
        # 로거 설정
        self.logger = logging.getLogger(__name__)
        
        # 데이터프레임 저장 (메모리 최적화를 위해 필요한 컬럼만 복사)
        self.df = df.copy()
        
        # 한글 폰트 설정
        self.font_prop = self._setup_korean_font()
        
        # matplotlib 및 seaborn 설정
        plt.style.use('dark_background')
        sns.set_style("darkgrid", {
            'axes.facecolor': '#343a40',
            'figure.facecolor': '#495057',
            'grid.color': '#495057',
            'text.color': 'white'
        })
        
        # Figure 설정
        self.figure = Figure(facecolor='#495057')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#343a40')
        
        # plotWidget에 캔버스 추가
        layout = QVBoxLayout(self.ui.plotWidget)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 컬럼 목록 설정
        self.setup_column_list()
        
        # 시그널 연결
        self.ui.columnList.currentItemChanged.connect(self.update_plot)
        self.ui.chartTypeComboBox.currentIndexChanged.connect(self.update_plot)
        
        # 첫 번째 컬럼 선택
        if self.ui.columnList.count() > 0:
            self.ui.columnList.setCurrentRow(0)
        
        # 윈도우 설정
        self.setWindowTitle("컬럼 분포 보기")
        self.resize(800, 600)
    
    def _setup_korean_font(self):
        """한글 폰트 설정"""
        try:
            if platform.system() == 'Windows':
                # Windows 한글 폰트 경로
                font_paths = [
                    'C:/Windows/Fonts/malgun.ttf',    # 맑은 고딕
                    'C:/Windows/Fonts/NanumGothic.ttf',  # 나눔고딕
                    'C:/Windows/Fonts/gulim.ttc',     # 굴림
                    'C:/Windows/Fonts/batang.ttc',    # 바탕
                ]
            else:
                # Linux/Mac 한글 폰트 경로
                font_paths = [
                    '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
                    '/usr/share/fonts/truetype/unfonts-core/UnDotum.ttf',
                    '/Library/Fonts/AppleGothic.ttf'
                ]
            
            # 사용 가능한 폰트 찾기
            font_path = None
            for path in font_paths:
                if os.path.exists(path):
                    font_path = path
                    break
            
            if font_path:
                # 폰트 추가
                fm.fontManager.addfont(font_path)
                font_prop = fm.FontProperties(fname=font_path)
                
                # 전역 폰트 설정
                plt.rcParams['font.family'] = font_prop.get_name()
                plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
                plt.rcParams['font.size'] = 10
                plt.rcParams['axes.titlesize'] = 12
                plt.rcParams['axes.labelsize'] = 10
                plt.rcParams['xtick.labelsize'] = 9
                plt.rcParams['ytick.labelsize'] = 9
                
                return font_prop
            else:
                self.logger.warning("한글 폰트를 찾을 수 없습니다. 시스템 기본 폰트를 사용합니다.")
                plt.rcParams['font.family'] = 'sans-serif'
                plt.rcParams['font.sans-serif'] = ['Malgun Gothic', 'NanumGothic', 'Arial Unicode MS']
                return None
                
        except Exception as e:
            self.logger.error(f"한글 폰트 설정 중 오류: {str(e)}")
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['font.sans-serif'] = ['Malgun Gothic', 'NanumGothic', 'Arial Unicode MS']
            return None
    
    def setup_column_list(self):
        """컬럼 목록을 설정합니다."""
        try:
            for column in self.df.columns:
                self.ui.columnList.addItem(str(column))  # 컬럼명을 문자열로 변환
        except Exception as e:
            self._show_error("컬럼 목록 설정 오류", str(e))
    
    def update_plot(self):
        """선택된 컬럼과 차트 유형에 따라 플롯을 업데이트합니다."""
        current_item = self.ui.columnList.currentItem()
        if not current_item:
            return
            
        column = current_item.text()
        chart_type = self.ui.chartTypeComboBox.currentText()
        
        try:
            # 메모리 사용량 최적화: 필요한 컬럼만 처리
            series = self.df[column]
            
            # 결측치 확인
            missing_count = series.isna().sum()
            total_count = len(series)
            missing_ratio = (missing_count / total_count) * 100
            
            # 이전 플롯 지우기
            self.ax.clear()
            
            if chart_type == "히스토그램":
                self._plot_histogram(series)
            elif chart_type == "박스플롯":
                self._plot_boxplot(series)
            elif chart_type == "바 차트":
                self._plot_bar(series)
                
            # 그래프 스타일 설정
            title = f"{column} 분포"
            if missing_count > 0:
                title += f"\n(결측치: {missing_count:,}개, {missing_ratio:.1f}%)"
            
            # 폰트 설정 적용
            if self.font_prop:
                self.ax.set_title(title, color='white', pad=20, fontsize=12, fontproperties=self.font_prop)
                self.ax.set_xlabel(self.ax.get_xlabel(), color='white', fontsize=10, fontproperties=self.font_prop)
                self.ax.set_ylabel(self.ax.get_ylabel(), color='white', fontsize=10, fontproperties=self.font_prop)
                
                # x축 레이블에 폰트 설정 적용
                if chart_type == "바 차트":
                    self.ax.set_xticklabels(self.ax.get_xticklabels(), rotation=45, fontsize=8, fontproperties=self.font_prop)
            else:
                self.ax.set_title(title, color='white', pad=20, fontsize=12)
                self.ax.set_xlabel(self.ax.get_xlabel(), color='white', fontsize=10)
                self.ax.set_ylabel(self.ax.get_ylabel(), color='white', fontsize=10)
                
                if chart_type == "바 차트":
                    self.ax.set_xticklabels(self.ax.get_xticklabels(), rotation=45, fontsize=8)
            
            self.ax.tick_params(colors='white', labelsize=10)
            for spine in self.ax.spines.values():
                spine.set_color('white')
                
            # 캔버스 업데이트
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            self._show_error("그래프 생성 오류", str(e))
    
    def _plot_histogram(self, series):
        """히스토그램을 그립니다."""
        if pd.api.types.is_numeric_dtype(series):
            # 이상치 제외 처리
            q1 = series.quantile(0.01)
            q3 = series.quantile(0.99)
            filtered_data = series[(series >= q1) & (series <= q3)]
            
            sns.histplot(data=filtered_data, ax=self.ax, color='#4dabf7')
            self.ax.set_xlabel(series.name, color='white', fontsize=10)
            self.ax.set_ylabel('빈도', color='white', fontsize=10)
        else:
            self._show_message("데이터 타입 오류", "숫자형 데이터만 히스토그램을 그릴 수 있습니다.")
    
    def _plot_boxplot(self, series):
        """박스플롯을 그립니다."""
        if pd.api.types.is_numeric_dtype(series):
            sns.boxplot(y=series, ax=self.ax, color='#4dabf7')
            self.ax.set_ylabel(series.name, color='white', fontsize=10)
        else:
            self._show_message("데이터 타입 오류", "숫자형 데이터만 박스플롯을 그릴 수 있습니다.")
    
    def _plot_bar(self, series):
        """바 차트를 그립니다."""
        value_counts = series.value_counts()
        if len(value_counts) > 50:
            self._show_message("데이터 오류", "고유값이 너무 많아 바 차트를 그릴 수 없습니다.\n(최대 50개)")
        else:
            value_counts.plot(kind='bar', ax=self.ax, color='#4dabf7')
            self.ax.set_xlabel(series.name, color='white', fontsize=10)
            self.ax.set_ylabel('빈도', color='white', fontsize=10)
            # x축 레이블 회전 및 폰트 크기 조정
            self.ax.tick_params(axis='x', rotation=45, labelsize=8)
    
    def _show_error(self, title, message):
        """에러 메시지를 표시합니다."""
        QMessageBox.critical(self, title, message)
        
    def _show_message(self, title, message):
        """정보 메시지를 표시합니다."""
        self.ax.text(0.5, 0.5, message,
                    ha='center', va='center', color='white',
                    transform=self.ax.transAxes)
        self.canvas.draw()