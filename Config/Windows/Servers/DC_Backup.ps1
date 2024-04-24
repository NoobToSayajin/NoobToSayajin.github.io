# Add-Content -Path C:\Users\Administrateur\Documents\script.ps1 -Value '
# Charge le module Active Directory s il n est pas déjà chargé
if (-not (Get-Module -Name ActiveDirectory)) {
    Import-Module NetSecurity
    Import-Module ActiveDirectory
}

# Definition du hostname
netdom renamecomputer $(hostname) /NewName:"DCBackup"

# Definition de l adresse IP
New-NetIPAddress -InterfaceAlias Ethernet0 -IPAddress 172.16.25.10 -PrefixLength 24 -DefaultGateway 172.16.25.254

# Definition du DNS
Set-DNSClientServerAddress -InterfaceAlias Ethernet0 -ServerAddresses 172.16.20.10,172.16.25.10,192.168.122.1

# Autorise le protocol ICMPv4 avec le DC Master
New-NetFirewallRule -DisplayName "ICMPv4 Allow DCMaster" -Direction Inbound -Protocol ICMPv4 -IcmpType 8 -RemoteAddress 172.16.20.10 -Action Allow

# Open SSH
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service -Name "sshd"
Set-Service -Name "sshd" -StartupType Automatic
# New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd) - Port 22' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22

# Creation du repertoire agent et recuperaton des agent.msi
New-Item -Path "c:\" -Name "agents" -ItemType "directory"

Copy-Item -Path \\DCMASTER\get\GLPI-Agent-1.6.1-x64.msi -Destination c:\agents\GLPI-Agent-1.6.1-x64.msi
Copy-Item -Path \\DCMASTER\get\zabbix_agent-6.4.11-windows-amd64-openssl.msi -Destination c:\agents\zabbix_agent-6.4.11-windows-amd64-openssl.msi
Copy-Item -Path \\DCMASTER\get\GLPI-AgentMonitor-x64.exe -Destination c:\agents\GLPI-AgentMonitor-x64.exe
# Copy-Item -Path \\DCMASTER\get\Nextcloud-3.12.3-x64.msi -Destination c:\agent\Nextcloud-3.12.3-x64.msi

# Installation des agents
msiexec /i "c:\agents\GLPI-Agent-1.6.1-x64.msi" /quiet SERVER=http://172.16.20.11/glpi ADD_FIREWALL_EXCEPTION=1 EXECMODE=1 DEBUG=1 RUNNOW=1 TASK_FREQUENCY=hourly
# Get-Content 'C:\Program Files\GLPI-Agent\logs\glpi-agent.log' -wait
msiexec /i "c:\agents\zabbix_agent-6.4.11-windows-amd64-openssl.msi" /quiet SERVER=127.0.0.1,172.16.20.12 SERVERACTIVE=127.0.0.1,172.16.20.12 LISTENIP=0.0.0.0 LISTENPORT=10050 HOSTNAME=$env:computername
# New-NetFirewallRule -DisplayName "Allow inbound 10050" -Direction Inbound -Protocol TCP -Action Allow -LocalPort 10050 -Profile Domain

# Joindre le domain
Add-Computer -DomainName NetForge.net -Credential NETFORGE\Administrateur -Restart -Force

# Active bureau a distance
Enable-PSRemoting -force
winrm quickconfig
# Certificat auto signe
New-SelfSignedCertificate -DnsName "DCBackup.netforge.net" -CertStoreLocation Cert:\LocalMachine\My
$cert = Get-ChildItem Cert:\LocalMachine\My | Where-Object{$_.Subject -eq "CN=DCBackup.netforge.net"}
winrm create winrm/config/Listener?Address=*+Transport=HTTPS '@{Hostname="DCBackup.netforge.net"; CertificateThumbprint='$cert.Thumbprint'}'

# Add a new firewall rule
New-NetFirewallRule -DisplayName "Windows Remote Management (HTTPS-In)" -Direction Inbound -Protocol TCP -RemoteAddress 172.16.20.10 -Action Allow -LocalPort 5986
New-NetFirewallRule -DisplayName "Windows Remote Management (HTTP-In)" -Direction Inbound -Protocol TCP -RemoteAddress 172.16.20.10 -Action Allow -LocalPort 5985
# New-NetFirewallRule -DisplayName "Autoriser le Bureau à distance (RDP)" -Group "Bureau à distance" -Profile Domain -Enabled True -Action Allow -LocalPort 5985


# Installation du roel ADDS
Install-WindowsFeature AD-Domain-Services -IncludeManagementTools

# Promouvoir en controleur
Install-ADDSDomainController

# Installation du role DHCP
Install-WindowsFeature DHCP -IncludeManagementTools