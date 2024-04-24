#!/usr/bin/bash

hostnamectl set-hostname Zabbix

echo "
127.0.0.1       localhost
127.0.1.1       Zabbix

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
    address 172.16.20.12
    netmask 255.255.255.0
    gateway 172.16.20.254
    dns-domain netforge.net
    dns-nameservers 172.16.20.10 172.16.25.10" > /etc/network/interfaces.d/ens33

systemctl restart networking

apt-get update && apt-get upgrade -y

# Installation des dependances
apt-get -y install apache2 php php-mysql php-mysqlnd php-ldap php-bcmath php-mbstring php-gd php-pdo php-xml libapache2-mod-php

# Installer et configurer la BDD
apt-get -y install mariadb-server mariadb-client
systemctl enable --now mariadb

# mysql_secure_installation
mysql -sfu root < "mysql_secure_installation.sql"

mysql -uroot -p'rootDBpass' -e "create database zabbix character set utf8mb4 collate utf8mb4_bin;"
mysql -uroot -p'rootDBpass' -e "create user 'zabbix'@'localhost' identified by 'zabbixDBpass';"
mysql -uroot -p'rootDBpass' -e "grant all privileges on zabbix.* to zabbix@localhost identified by 'zabbixDBpass';"

# Installer et configurer le serveur Zabbix
# wget https://repo.zabbix.com/zabbix/6.0/debian/pool/main/z/zabbix-release/zabbix-release_6.0-4+debian$(cut -d"." -f1 /etc/debian_version)_all.deb

# dpkg -i zabbix-release_6.0-4+debian$(cut -d"." -f1 /etc/debian_version)_all.deb

wget https://repo.zabbix.com/zabbix/6.4/debian/pool/main/z/zabbix-release/zabbix-release_6.4-1+debian12_all.deb

dpkg -i zabbix-release_6.4-1+debian12_all.deb

apt-get update

apt-get -y install zabbix-server-mysql zabbix-frontend-php zabbix-apache-conf zabbix-sql-scripts zabbix-agent

zcat /usr/share/zabbix-sql-scripts/mysql/server.sql.gz | mysql --default-character-set=utf8mb4 -uzabbix -p'zabbixDBpass' zabbix

# Ajout du mot de passe dans la conf BDD
echo "DBPassword=zabbixDBpass" >> /etc/zabbix/zabbix_server.conf

mysql -uroot -p'rootDBpass' -e "set global log_bin_trust_function_creators = 0;"

# Redemarrage de zabbix
systemctl restart zabbix-server zabbix-agent 
systemctl enable zabbix-server zabbix-agent

# Editer la timezone dans la config php.ini
sed -i 's;#\ php_value\ date.timezone\ Europe\/Riga;php_value date.timezone\ Europe\/Paris;g' /etc/zabbix/apache.conf

echo "
<VirtualHost *:80>
        ServerAdmin webmaster@localhost
        DocumentRoot /usr/share/zabbix

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost> " >> /etc/apache2/sites-available/zabbix.conf

a2dissite 000-default.conf
a2ensite zabbix.conf

systemctl reload apache2

# Redemarrage de apache
systemctl restart apache2
systemctl enable apache2
