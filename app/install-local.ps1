param([string]$BuildDir = (Join-Path $PSScriptRoot '..\build\BlogManager'), [string]$BrowsersDir)
$ErrorActionPreference = 'Stop'
$programDir = Join-Path ([Environment]::GetFolderPath('Desktop')) '블로그 발행 관리자'
$runtimeDir = Join-Path $env:LOCALAPPDATA 'NaverBlogManager'
$stateDir = Join-Path $runtimeDir 'data'
$browserDir = Join-Path $runtimeDir 'browsers'
if (!(Test-Path -LiteralPath (Join-Path $BuildDir 'BlogManager.exe'))) { throw '실행 파일 빌드가 필요합니다.' }
New-Item -ItemType Directory -Force -Path $programDir,$stateDir,$browserDir | Out-Null
# Keep session state outside the OneDrive Desktop and restrict access to the owner.
$taskOwnerSid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
& icacls.exe $stateDir /inheritance:r /grant:r "*${taskOwnerSid}:(OI)(CI)F" '*S-1-5-18:(OI)(CI)F' '*S-1-5-32-544:(OI)(CI)F' | Out-Null
if ($LASTEXITCODE -ne 0) { throw '데이터 폴더 권한 설정에 실패했습니다.' }
Copy-Item -Path (Join-Path $BuildDir '*') -Destination $programDir -Recurse -Force
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'README.md') -Destination (Join-Path $programDir '사용 안내.md') -Force
if ($BrowsersDir) {
    Copy-Item -Path (Join-Path $BrowsersDir '*') -Destination $browserDir -Recurse -Force
}
$configPath = Join-Path $stateDir 'config.json'
if (Test-Path -LiteralPath $configPath) { $config = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json }
else { $config = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'config.json') -Raw -Encoding UTF8 | ConvertFrom-Json }
$codexCommand = Get-Command codex.exe -ErrorAction SilentlyContinue
$codexExe = if ($codexCommand) { $codexCommand.Source } else {
    Get-ChildItem -LiteralPath (Join-Path $env:LOCALAPPDATA 'OpenAI\Codex\bin') -Filter codex.exe -Recurse | Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName
}
if (!$codexExe) { throw 'Codex 실행 파일을 찾지 못했습니다.' }
$config | Add-Member -Force NoteProperty codex_path $codexExe
$config | Add-Member -Force NoteProperty browser_path $browserDir
$config | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath $configPath -Encoding UTF8
$exe = Join-Path $programDir 'BlogManager.exe'
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut((Join-Path $programDir '관리 화면.lnk'))
$shortcut.TargetPath = $exe
$shortcut.Arguments = '--open --state-dir "' + $stateDir + '"'
$shortcut.WorkingDirectory = $programDir
$shortcut.Save()
$startup = Join-Path ([Environment]::GetFolderPath('Startup')) 'N100 Blog Manager.lnk'
$shortcut = $shell.CreateShortcut($startup)
$shortcut.TargetPath = $exe
$shortcut.Arguments = '--background --state-dir "' + $stateDir + '"'
$shortcut.WorkingDirectory = $programDir
$shortcut.Save()
Start-Process -FilePath $exe -ArgumentList ('--background --state-dir "' + $stateDir + '"') -WindowStyle Hidden
[pscustomobject]@{program=$programDir;state=$stateDir;autostart='Windows 로그인 후 자동 실행';boot='관리 UI에서 Windows 자격 증명으로 별도 등록'} | ConvertTo-Json
