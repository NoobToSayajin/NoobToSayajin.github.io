#!/usr/bin/bash

hostnamectl set-hostname Syslog

echo "
127.0.0.1       localhost
127.0.1.1       Syslog

# The following lines are desirable for IPv6 capable hosts
::1     localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
" >> /etc/hosts

echo "
# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface" > /etc/network/interfaces

echo "
auto ens33
iface ens33  inet static
    address 172.16.25.12
    netmask 255.255.255.0
    gateway 172.16.25.254
    dns-domain netforge.net
    dns-nameservers 172.16.20.10 172.16.25.10" > /etc/network/interfaces.d/ens33

systemctl restart networking

# Ajout du hostname dans la configuration zabbix
sed -i 's;Hostname=Zabbix\ server;Hostname=Syslog;g' /etc/zabbix/zabbix_agentd.conf
systemctl restart agent-zabbix

apt-get update && apt-get upgrade -y

apt-get install -y apache2 mariadb-server php php-mysql php-gd
apt-get install rsyslog-mysql -y

# mysql -sfu root < "mysql_secure_installation.sql" # ne fonctionne pas
mariadb-secure-installation <<EOF

y
y
Soleil1
Soleil1
y
y
y
y
EOF

mariadb -uroot -p'Soleil1' -e "GRANT ALL PRIVILEGES ON Syslog . * TO 'rsyslog'@'localhost';"

sed -i 's;#module(load="imudp");module(load="imudp");g' /etc/rsyslog.conf
sed -i 's;#input(type="imudp" port="514");input(type="imudp" port="514");g' /etc/rsyslog.conf
sed -i 's;#module(load="imtcp");module(load="imtcp");g' /etc/rsyslog.conf
sed -i 's;#input(type="imtcp" port="514");input(type="imtcp" port="514");g' /etc/rsyslog.conf

echo -e "\n*.* :ommysql:localhost,Syslog,rsyslog,Soleil1" >> /etc/rsyslog.conf

ufw enable
ufw allow 514
ufw reload

systemctl enable rsyslog

# verif mdp
# mysql -e "SELECT User,Password, Host FROM mysql.user;"
# GRANT ALL PRIVILEGES ON *.* TO `root`@`localhost` IDENTIFIED VIA mysql_native_password USING 'invalid' OR unix_socket WITH GRANT OPTION