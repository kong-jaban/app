!include "MUI2.nsh"

; 버전 정보
!define VERSION "1.0"
!define REVISION "202504_1"

; 기본 설정
Name "S-DIA"
OutFile "dist\S-DIA_Setup-v${VERSION}-r${REVISION}.exe"
InstallDir "$PROGRAMFILES64\S-DIA"
RequestExecutionLevel admin

!define MUI_ABORTWARNING
!define APP_DATA_DIR "$LOCALAPPDATA\UPSDATA\S-DIA"

; 페이지 설정
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; 언어 설정
!insertmacro MUI_LANGUAGE "Korean"

Function .onInit
    ; 관리자 권한 확인
    UserInfo::GetAccountType
    Pop $0
    ${If} $0 != "admin"
        MessageBox MB_OK|MB_ICONEXCLAMATION "이 설치 프로그램은 관리자 권한이 필요합니다."
        Abort
    ${EndIf}
    
    ; 기존 프로그램 종료
    ExecWait 'taskkill /F /IM S-DIA.exe' $0
FunctionEnd

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    
    ; 실행 중인 S-DIA 프로세스 종료
    ExecWait 'taskkill /F /IM S-DIA.exe'
    
    ; 파일 복사
    File "dist\S-DIA.exe"
    
    ; 데이터 디렉토리 생성
    CreateDirectory "${APP_DATA_DIR}"
    
    ; 시작 메뉴 바로가기 생성
    CreateDirectory "$SMPROGRAMS\S-DIA"
    CreateShortcut "$SMPROGRAMS\S-DIA\S-DIA.lnk" "$INSTDIR\S-DIA.exe"
    CreateShortcut "$DESKTOP\S-DIA.lnk" "$INSTDIR\S-DIA.exe"
    
    ; 제거 정보 등록
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; 프로그램 정보 등록
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\S-DIA" \
                     "DisplayName" "S-DIA"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\S-DIA" \
                     "DisplayVersion" "v${VERSION}-r${REVISION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\S-DIA" \
                     "Publisher" "UPSDATA"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\S-DIA" \
                     "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\S-DIA" \
                      "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\S-DIA" \
                      "NoRepair" 1
SectionEnd

Section "Uninstall"
    ; 실행 중인 S-DIA 프로세스 종료
    ExecWait 'taskkill /F /IM S-DIA.exe'
    
    ; 프로그램 파일 삭제
    Delete "$INSTDIR\S-DIA.exe"
    Delete "$INSTDIR\uninstall.exe"
    
    ; 시작 메뉴 바로가기 삭제
    Delete "$SMPROGRAMS\S-DIA\S-DIA.lnk"
    RMDir "$SMPROGRAMS\S-DIA"
    
    ; 바탕화면 바로가기 삭제
    Delete "$DESKTOP\S-DIA.lnk"
    
    ; 설치 디렉토리 삭제
    RMDir "$INSTDIR"
    
    ; 프로그램 정보 삭제
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\S-DIA"
    
    ; 데이터 디렉토리는 유지 (사용자 데이터 보존)
    ; RMDir /r "$LOCALAPPDATA\UPSDATA\S-DIA"
SectionEnd 