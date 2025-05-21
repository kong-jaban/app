# 코드 서명 스크립트
param(
    [Parameter(Mandatory=$true)]
    [string]$FilePath,
    
    [Parameter(Mandatory=$false)]
    [string]$Description = "S-DIA Application"
)

$certPath = Join-Path $PSScriptRoot "test_cert.pfx"
$password = "password"

# 인증서 로드
$pwd = ConvertTo-SecureString -String $password -Force -AsPlainText
$cert = Get-PfxCertificate -FilePath $certPath -Password $pwd

# 코드 서명
Set-AuthenticodeSignature -FilePath $FilePath -Certificate $cert -TimestampServer "http://timestamp.digicert.com"

Write-Host "코드 서명이 완료되었습니다: $FilePath" 