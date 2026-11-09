# Builds dist/app/app.exe and copies the private runtime files into it.
# Usage: powershell -ExecutionPolicy Bypass -File build.ps1
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

# A running instance locks files in dist/app and makes the build fail.
Get-Process app -ErrorAction SilentlyContinue |
    Where-Object { $_.Path -like "$PSScriptRoot\dist\app\*" } |
    Stop-Process -Force
Start-Sleep -Seconds 1

# PyInstaller logs to stderr; run through cmd so PowerShell doesn't treat it as an error.
cmd /c "poetry run pyinstaller app.spec --noconfirm --clean > build.log 2>&1"
if ($LASTEXITCODE -ne 0) {
    Get-Content build.log -Tail 20
    throw "PyInstaller failed (exit $LASTEXITCODE). See build.log"
}

Copy-Item config.json dist\app\ -Force
New-Item -ItemType Directory -Force dist\app\src\db | Out-Null
Copy-Item src\db\extra_features.sqlite dist\app\src\db\ -Force

Write-Host "Build OK: dist\app\app.exe"
