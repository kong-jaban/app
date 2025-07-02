@echo off
chcp 65001 > nul
echo S-DIA 빌드 시작...

:: Python 가상환경 활성화 (있는 경우)
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

:: 필요한 패키지 설치
echo 필요한 패키지 설치 중...
pip install -r requirements.txt

:: PyInstaller로 실행 파일 생성
echo 실행 파일 생성 중...
pyinstaller S-DIA.spec

:: NSIS로 설치 패키지 생성
echo 설치 패키지 생성 중...
makensis installer.nsi

echo 빌드 완료!
pause 