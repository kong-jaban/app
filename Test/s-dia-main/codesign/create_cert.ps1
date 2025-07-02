# 인증서 생성 스크립트
$certName = "S-DIA Test Certificate"
$certPath = "Cert:\CurrentUser\My"
$pfxPath = Join-Path $PSScriptRoot "test_cert.pfx"
$password = "password"

# 인증서 생성
$cert = New-SelfSignedCertificate -DnsName $certName -CertStoreLocation $certPath -Type CodeSigningCert -KeyUsage DigitalSignature -FriendlyName $certName

# PFX 파일로 내보내기
$pwd = ConvertTo-SecureString -String $password -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $pwd

Write-Host "인증서가 생성되었습니다: $pfxPath" 