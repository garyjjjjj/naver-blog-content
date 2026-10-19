param(
    [Parameter(Mandatory=$true)][string]$StateDir,
    [Parameter(Mandatory=$true)][string]$Python,
    [Parameter(Mandatory=$true)][string]$Manager,
    [string]$Owner = '',
    [switch]$Elevated,
    [switch]$Frozen
)
$ErrorActionPreference = 'Stop'
if (-not $Owner) { $Owner = [Security.Principal.WindowsIdentity]::GetCurrent().Name }
$currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
$currentPrincipal = [Security.Principal.WindowsPrincipal]::new($currentIdentity)
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    $taskArguments = @('-NoProfile','-ExecutionPolicy','Bypass','-File',('"'+$PSCommandPath+'"'),'-StateDir',('"'+$StateDir+'"'),'-Python',('"'+$Python+'"'),'-Manager',('"'+$Manager+'"'),'-Owner',('"'+$Owner+'"'),'-Elevated')
    if ($Frozen) { $taskArguments += '-Frozen' }
    try {
        Start-Process -FilePath 'powershell.exe' -Verb RunAs -ArgumentList $taskArguments -WindowStyle Hidden -Wait
    } catch {
        [IO.File]::WriteAllText((Join-Path $StateDir 'autostart-setup.json'), '{"ok":false,"error":"Windows administrator approval was cancelled."}')
    }
    exit
}
try {
    Add-Type -AssemblyName System.Windows.Forms
    $credential = Get-Credential -UserName $Owner -Message 'N100 blog manager: enter the WINDOWS account password for startup BEFORE sign-in. This is not the Naver password or Windows PIN. The password is stored by Windows Task Scheduler only.'
    if (-not $credential) { throw 'Setup cancelled.' }
    if ($credential.UserName -ne $Owner) { throw 'Use the same Windows account that owns the manager.' }
    $taskArgs = if ($Frozen) { '--background --state-dir "'+$StateDir+'"' } else { '"'+$Manager+'" --background --state-dir "'+$StateDir+'"' }
    $action = New-ScheduledTaskAction -Execute $Python -Argument $taskArgs -WorkingDirectory (Split-Path -Parent $Python)
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $trigger.Delay = 'PT30S'
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    $taskDefinition = New-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -Description 'N100 Blog Publisher Manager: local dashboard and GitHub monitor. Publication stays gated until verified.'
    $taskPassword = $credential.GetNetworkCredential().Password
    Register-ScheduledTask -TaskName 'N100BlogPublisherManager' -InputObject $taskDefinition -User $credential.UserName -Password $taskPassword -Force | Out-Null
    $taskPassword = $null
    $credential = $null
    [IO.File]::WriteAllText((Join-Path $StateDir 'autostart-setup.json'), '{"ok":true,"message":"Boot task registered. Reboot verification still required."}')
    [System.Windows.Forms.MessageBox]::Show('Boot startup has been registered. The manager will start 30 seconds after Windows boots. Please verify after the next restart.','Blog Manager') | Out-Null
} catch {
    [IO.File]::WriteAllText((Join-Path $StateDir 'autostart-setup.json'), (@{ok=$false;error=$_.Exception.Message} | ConvertTo-Json -Compress))
    [System.Windows.Forms.MessageBox]::Show($_.Exception.Message,'Blog Manager setup') | Out-Null
}
