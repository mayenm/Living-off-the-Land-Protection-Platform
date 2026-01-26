# Install-Sysmon.ps1
# Automates Sysmon installation with OGT WatchTower configuration

$SysmonUrl = "https://download.sysinternals.com/files/Sysmon.zip"
$ZipPath = "$env:TEMP\Sysmon.zip"
$ExtractPath = "$env:TEMP\Sysmon"
$ConfigUrl = "https://raw.githubusercontent.com/SwiftOnSecurity/sysmon-config/master/sysmonconfig-export.xml" # Using SwiftOnSecurity as base
$ConfigPath = "$PSScriptRoot\sysmonproxy.xml"

Write-Host "[*] Downloading Sysmon..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $SysmonUrl -OutFile $ZipPath

Write-Host "[*] Extracting Sysmon..." -ForegroundColor Cyan
Expand-Archive -Path $ZipPath -DestinationPath $ExtractPath -Force

if (-not (Test-Path $ConfigPath)) {
    Write-Host "[*] Downloading Base Config (SwiftOnSecurity)..." -ForegroundColor Cyan
    try {
        Invoke-WebRequest -Uri $ConfigUrl -OutFile $ConfigPath
    }
    catch {
        Write-Host "[!] Failed to download config. Creating minimal config." -ForegroundColor Yellow
        $MinimalConfig = @"
<Sysmon schemaversion="4.82">
  <HashAlgorithms>*</HashAlgorithms>
  <EventFiltering>
    <!-- Event ID 1: Process Creation (Log everything for visibility) -->
    <ProcessCreate onmatch="exclude">
    </ProcessCreate>
    <!-- Event ID 3: Network Connection -->
    <NetworkConnect onmatch="include">
        <Image condition="end with">certutil.exe</Image>
        <Image condition="end with">powershell.exe</Image>
        <Image condition="end with">mshta.exe</Image>
    </NetworkConnect>
    <!-- Event ID 11: FileCreate -->
    <FileCreate onmatch="include">
        <Image condition="end with">certutil.exe</Image>
    </FileCreate>
  </EventFiltering>
</Sysmon>
"@
        Set-Content -Path $ConfigPath -Value $MinimalConfig
    }
}

Write-Host "[*] Installing/Updating Sysmon..." -ForegroundColor Cyan
$SysmonExe = "$ExtractPath\Sysmon64.exe"
if (-not (Test-Path $SysmonExe)) {
    $SysmonExe = "$ExtractPath\Sysmon.exe"
}

Start-Process -FilePath $SysmonExe -ArgumentList "-accepteula -i `"$ConfigPath`"" -Wait -Verb RunAs

Write-Host "[+] Sysmon Installed/Updated Successfully!" -ForegroundColor Green
Write-Host "    Verifying service status..."
Get-Service Sysmon64 -ErrorAction SilentlyContinue | Select-Object Status, Name, DisplayName
