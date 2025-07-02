# S-DIA Windows Application

PySide6를 사용한 Windows 데스크톱 애플리케이션입니다.

## 설치 방법

1. Python 3.8 이상이 설치되어 있어야 합니다.

2. 가상환경 설정:
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## 실행 방법

```bash
python src/main.py
```

## 프로젝트 구조

- `src/`: 소스 코드
  - `ui/`: 사용자 인터페이스 관련 코드
  - `core/`: 핵심 애플리케이션 로직
  - `utils/`: 유틸리티 함수들
- `resources/`: 리소스 파일들 (스타일시트, 이미지 등)
- `venv/`: Python 가상환경 디렉토리 (자동 생성됨)

## 코드 서명

### 인증서 생성
1. `codesign` 폴더로 이동합니다.
2. `create_cert.bat`를 실행하여 테스트 인증서를 생성합니다.
   - 생성된 인증서는 `codesign/test_cert.pfx`에 저장됩니다.
   - 기본 비밀번호는 "password"입니다.

### 코드 서명
1. 수동으로 실행하는 경우:
   - `codesign/sign_code.bat`를 실행하고 서명할 파일의 경로를 지정합니다.
   - 예: `sign_code.bat "path/to/file.exe"`

2. 빌드 시 자동 실행:
   - PyInstaller로 빌드하면 자동으로 코드 서명이 실행됩니다.
   - `S-DIA.spec` 파일에 빌드 후 코드 서명 훅이 포함되어 있습니다.

### 참고사항
- 테스트 인증서는 개발 및 테스트 목적으로만 사용하세요.
- 프로덕션 환경에서는 신뢰할 수 있는 인증서를 사용하세요.
- 인증서 관련 파일들은 `codesign` 폴더에서 관리됩니다. 