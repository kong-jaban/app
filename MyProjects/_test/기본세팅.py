import os
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtWidgets import *
from PyQt5 import uic
# 더 추가할 필요가 있다면 추가하시면 됩니다. 예: (from PyQt5.QtGui import QIcon)

#파일 경로설정
def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))    
    return os.path.join(base_path, relative_path)
#이부분 역할 : pyinstaller를 통해 하나의 exe파일로 컴파일링할때
#리소스들의 위치가 실행파일 위치 기준이 아니라 
#sys._MEIPASS를 통해 리소스를 불러오도록 하기위함. 

#자세히>
#getattr 메서드는 이름에 해당하는 객체 속성의 값을 가져오는 Build-in 함수
#getattr(sys,"_MEIPASS",default) 의 경우는 sys모듈의 _MEIPASS 멤버함수가 있을경우 sys._MEIPASS 값을 가져오고 아니면 default를 가져오는 코드
#default에 사용된 메서드에서 __file__은 해당 코드를 가지는 파이썬 파일의 경로이며, 실행한 위치에서의 상대경로를 포함
# os.path.abspath( )는 절대경로를 구하는 메서드이며
# os.path.abspath(__file__)은 현재 파일의 절대경로를 구합
# os.path.dirname( )메서드는 현재 파일이 포함된 폴더의 경로를 구하는 메서드
# os.path.join( ) 메서드는 두 경로를 합치는 메서드

#ui파일을 class형태로 변환부
form = resource_path('main.ui')
form_class = uic.loadUiType(form)[0]

#파일 경로설정부분에서 만든 resource_path함수를 통해
# main.ui경로를 form변수에 입력.

#uic.loadUiType 메서드를 통해 해당 ui파일을 class형태로 변환
#0번은 Ui_MainWindow클래스, 1번은 PyQt6.QtWidgets.QMainWindow인데
#uic.loadUiType(form)[0]을 통해 0번으로 선택하여 form_class변수에 입력

#class설정 부분
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super( ).__init__( )
        self.setupUi(self)

        # 여기에 시그널, 설정 
    #여기에 함수 설정
# QMainWindow와 ui파일을 class형태로 변환시킨 form_class를 WindowClass에 다중상속.
# 여기서 def __init__(self)는 class가 호출되었을때 초기값을 의미. 
# super()메서드는 부모클래스를 상속받는 메서드인데
#  super().__init__()를 통해 부모클래스 초기값 호출.
# 그리고 self.setupUi(self)메서드를 통해
# 구성한 UI를 화면에 출력

#app생성부
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = WindowClass( )
    myWindow.show( )
    app.exec_( )
#if __name__ == '__main__': 부분은 이 파일을 여기서 실행할 경우를 의미합니다.(다른 파일에서의 호출이 아닌)
#app = QApplication(sys.argv)에서 sys.argv는 프로그램을 실행할 때 입력된 값을 읽는 메서드
# 여기서는 작업중인 py파일의 절대 경로를 의미
#QAplication()클래스는 GUI응용프로그램의 제어, 흐름과기본설정들을
# 관리하며, 모든 이벤트 처리 전달하는 메인이벤트 류프를 포함한
# 응용프로그램의 초기화, 마무리, 세션관리를 제공.
# ->GUI의 전반적인것 포함한 클래스이며,
#  QApplication(sys.argv)는 간단히 QApplication객체가 실행할 파일이
# 현재파이썬 코드라는 것을 의미

#결과적으로 app=QApplication(sys.argv) app이 생성됨을 의미
# 그리고 myWindow = WindowClass( )를 통해 designer을 통해 만들었던 ui파일을 출력하는 class로
# myWindow 인스턴스를 생성해주고 myWindow.show( )를 통해 해당 ui를 화면에 출력

# app.exec_( )는 app의 무한 루프를 의미합니다.
# app생성 후 루프 설정을 해주지 않으면,
# 코드의 마지막에서 종료하게 됩니다.
# 때문에 app.exec_( )를 통해 종료되지 않도록 루프를 설정합니다.
# app이 종료되는 경우 0을 반환하여 종료하게됩니다.

