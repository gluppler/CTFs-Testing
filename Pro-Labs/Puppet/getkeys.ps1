$ErrorActionPreference = "Continue"
Write-Host "=== DC IT Share ==="
Get-ChildItem \\dc01.puppet.vl\it
Write-Host "=== SSH Keys ==="
Get-ChildItem \\dc01.puppet.vl\it\.ssh
Copy-Item \\dc01.puppet.vl\it\.ssh\ed25519 C:\programdata\puppet\ed25519 -Force
Copy-Item \\dc01.puppet.vl\it\.ssh\ed25519.pub C:\programdata\puppet\ed25519.pub -Force
Write-Host "=== DONE ==="
