#!/usr/bin/bash

hostnamectl set-hostname GLPI

echo "
127.0.0.1       localhost
127.0.1.1       GLPI

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
    address 172.16.20.11
    netmask 255.255.255.0
    gateway 172.16.20.254
    dns-domain netforge.net
    dns-nameservers 172.16.20.10 172.16.25.10" > /etc/network/interfaces.d/ens33

systemctl restart networking

# Ajout du hostname dans la configuration zabbix
sed -i 's;Hostname=Zabbix\ server;Hostname=GLPI;g' /etc/zabbix/zabbix_agentd.conf
systemctl restart agent-zabbix

# Mise a jour du system
apt-get update && apt-get upgrade -y

# Installation de Apache2 et PHP
# Apache2
apt-get install apache2 -y
systemctl enable apache2.service
echo 'ServerName $(hostname)' >> /etc/apache2/conf-available/fqdn.conf

a2enconf fqdn

systemctl reload apache2

# PHP
apt-get install php -y

systemctl reload apache2

# Installation de MariaDB
apt-get install mariadb-server -y 
systemctl enable mariadb.service

# Creation de la BDD
mariadb -uroot -p'Soleil1' -e "CREATE DATABASE glpi;"
mariadb -uroot -p'Soleil1' -e "CREATE USER 'glpibdd'@'localhost' IDENTIFIED BY 'Soleil1';"
mariadb -uroot -p'Soleil1' -e "GRANT ALL PRIVILEGES ON glpi . * TO 'glpibdd'@'localhost';"

apt-get install perl -y
apt-get install php-ldap php-imap php-apcu php-xmlrpc php-cas php-mysqli php-mbstring php-curl php-gd php-simplexml php-xml php-intl php-zip php-bz2 -y
service apache2 reload
cd /tmp
wget https://github.com/glpi-project/glpi/releases/download/10.0.9/glpi-10.0.9.tgz
tar xzf glpi-10.0.9.tgz
cp -R /tmp/glpi /usr/share
chown -R root.www-data /usr/share/glpi
chmod -R 775 /usr/share/glpi
ln -s /usr/share/glpi /var/www/html/

echo "
<VirtualHost *:80>
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html/glpi

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost> " >> /etc/apache2/sites-available/glpi.conf

a2dissite 000-default.conf
a2ensite glpi.conf

systemctl reload apache2

if [[ -f /usr/share/glpi/config/config_db.php ]]; then
    rm /usr/share/glpi/install/install.php
    echo "suppression"
else
    echo "Finir l'installtion via la page web"
fi