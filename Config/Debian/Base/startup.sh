#!/usr/bin/bash

apt-get update && apt-get upgrade -y

echo "
alias ll='ls -lrt'
" > ~/.bashrc

source ~/.bashrc

echo "

domain NetForge.fr
search NetForge.fr
nameserver 172.16.20.10
nameserver 172.16.25.10

" >> /etc/resolv.conf

apt-get install -y sudo ufw perl

# Zabbix Agent
wget https://repo.zabbix.com/zabbix/6.4/debian/pool/main/z/zabbix-release/zabbix-release_6.4-1+debian12_all.deb
dpkg -i zabbix-release_6.4-1+debian12_all.deb
apt-get update && apt-get install zabbix-agent -y

systemctl enable ufw
systemctl enable zabbix-agent
systemctl start zabbix-agent

ufw allow 10050
ufw reload

sed -i 's;Server=127.0.0.1;Server=127.0.0.1,172.16.20.12;g' /etc/zabbix/zabbix_agentd.conf
sed -i 's;#\ ListenPort=10050;ListenPort=10050;g' /etc/zabbix/zabbix_agentd.conf
sed -i 's;#\ ListenIP=0.0.0.0;ListenIP=0.0.0.0;g' /etc/zabbix/zabbix_agentd.conf
sed -i 's;ServerActive=127.0.0.1;ServerActive=127.0.0.1,172.16.20.12;g' /etc/zabbix/zabbix_agentd.conf
# sed -i 's;Hostname=Zabbix\ server;Hostname=nextcloud;g' /etc/zabbix/zabbix_agentd.conf

# GLPI Agent
# wget https://github.com/glpi-project/glpi-agent/releases/download/1.6.1/glpi-agent-1.6.1-linux-installer.pl

# /etc/glpi-agent/conf.d/00-install.cfg
perl glpi-agent-1.7-linux-installer.pl <<EOF



EOF
echo 'server = http://172.16.20.11/glpi' >> /etc/glpi-agent/conf.d/00-install.cfg

ufw allow 62354
ufw allow 389
ufw allow 3628
# ufw allow 636
# ufw allow 3629
ufw reload

systemctl restart glpi-agent

apt-get install -y realmd sssd sssd-tools libnss-sss libpam-sss adcli samba-common samba-common-bin oddjob oddjob-mkhomedir packagekit krb5-user resolvconf

# chown root:root /etc/sssd/sssd.conf
# chmod 600 /etc/sssd/sssd.conf

realm join --user=Administrateur NETFORGE.NET << EOF
Soleil1
EOF

# ligne a changer
sed -i 's;use_fully_qualified_names\ =\ True;use_fully_qualified_names\ =\ False;g' /etc/sssd/sssd.conf
# sed -i 's;ldap_id_mapping\ =\ True;ldap_id_mapping\ =\ True;g' /etc/sssd/sssd.conf
echo "
ldap_user_uid_number = uidNumber
ldap_user_gid_number = gidNumber" >> /etc/sssd/sssd.conf

# sed -i '/default_realm = NETFORGE.NET/a \
# dns_lookup_kdc = true\
# dns_lookup_realm = true' /etc/krb5.conf

# pam-auth-update --enable mkhomedir

rm -f /var/lib/sss/db/*
systemctl restart sssd
realm permit -g GG_Administrateur_Linux@netforge.net


# echo "%NETFORGE.NET\\Admin\\Administrateur_Linux\\GG_Administrateur_Linux ALL=(ALL:ALL) ALL" >> /etc/sudoers.d/GG_Administrateur_Linux
echo "%GG_Administrateur_Linux ALL=(ALL:ALL) ALL" >> /etc/sudoers.d/GG_Administrateur_Linux
