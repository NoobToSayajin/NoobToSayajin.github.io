# Add-Content -Path C:\Users\Administrateur\Documents\script.ps1 -Value '
# Charge le module Active Directory s il n est pas déjà chargé
if (-not (Get-Module -Name ActiveDirectory)) {
    Import-Module NetSecurity
    Import-Module ActiveDirectory
}

# Write-Host O | netdom renamecomputer $(hostname) /NewName:"DCBackup"
netdom renamecomputer $(hostname) /NewName:"DCBackup"

# Recup la config IP
[Environment]::MachineName
Get-NetIPConfiguration
Get-NetIPConfiguration | Select-Object InterfaceIndex

# Definir l adresse IP
New-NetIPAddress -InterfaceAlias Ethernet0 -IPAddress 172.16.25.10 -PrefixLength 24 -DefaultGateway 172.16.25.254

# Definir DNS
Set-DNSClientServerAddress -InterfaceAlias Ethernet0 -ServerAddresses 172.16.20.10,172.16.25.10

# Autorise le protocol ICMPv4 avec le DC Master
New-NetFirewallRule -DisplayName "ICMPv4 Allow DCMaster" -Direction Inbound -Protocol ICMPv4 -IcmpType 8 -RemoteAddress 172.16.20.10 -Action Allow

# Remove-NetFirewallRule -DisplayName "ICMPv4 Allow"

# Joindre le domain
Add-Computer -DomainName NetForge.net -Credential NETFORGE\Administrateur -Restart -Force

# Active bureau a distance
Enable-PSRemoting

# Installation du roel ADDS
Install-WindowsFeature AD-Domain-Services -IncludeManagementTools

# Promouvoir en controleur
Install-ADDSDomainController

# Installation du role DHCP
Install-WindowsFeature DHCP -IncludeManagementTools