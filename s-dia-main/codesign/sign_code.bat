@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0sign_code.ps1" -FilePath "%~1"
pause 