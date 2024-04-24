#!/usr/bin/bash

hostnamectl set-hostname Nextcloud

echo "
127.0.0.1       localhost
127.0.1.1       Nextcloud

# The following lines are desirable for IPv6 capable hosts
::1     localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
" > /etc/hosts

echo "
# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface" > /etc/network/interfaces

echo "
auto ens33
iface ens33  inet static
    address 172.16.25.11
    netmask 255.255.255.0
    gateway 172.16.25.254
    dns-domain netforge.net
    dns-nameservers 172.16.20.10 172.16.25.10" > /etc/network/interfaces.d/ens33

systemctl restart networking

# Ajout du hostname dans la configuration zabbix
sed -i 's;Hostname=Zabbix\ server;Hostname=Nextcloud;g' /etc/zabbix/zabbix_agentd.conf
systemctl restart agent-zabbix

apt-get update && apt-get upgrade -y

# Installation apache
apt-get install apache2 -y

# Installation ufw firewall
apt-get install ufw -y
ufw allow 22
ufw enable -y
ufw app list
ufw allow "WWW Full"
ufw reload

# Installation PHP
apt install software-properties-common ca-certificates lsb-release apt-transport-https -y
sh -c 'echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list'
wget -qO - https://packages.sury.org/php/apt.gpg | apt-key add -
apt-get update
pat-get purge -y php7*
pat-get purge -y php8*
apt-get install -y php8.3 php-curl php-cli php-mysql php-gd php-common php-xml php-json php-intl php-pear php-imagick php-dev php-common php-mbstring php-zip php-soap php-bz2 php-bcmath php-gmp php-apcu libmagickcore-dev php-redis php-memcached php-ldap

sed -i 's#;date.timezone\ =#date.timezone\ =\ Europe\/Paris#g' /etc/php/8.3/apache2/php.ini
sed -i 's#memory_limit\ =\ 128M#memory_limit\ =\ 512M#g' /etc/php/8.3/apache2/php.ini
sed -i 's#upload_max_filesize\ =\ 2M#upload_max_filesize\ =\ 500M#g' /etc/php/8.3/apache2/php.ini
sed -i 's#post_max_size\ =\ 8M#post_max_size\ =\ 600M#g' /etc/php/8.3/apache2/php.ini
sed -i 's#max_execution_time\ =\ 30#max_execution_time\ =\ 300#g' /etc/php/8.3/apache2/php.ini

# sed -i 's#;file_uploads\ =\ On#file_uploads\ =\ On#g' /etc/php/8.3/apache2/php.ini
# sed -i 's#;allow_url_fopen\ =\ On#allow_url_fopen\ =\ On#g' /etc/php/8.3/apache2/php.ini

# sed -i 's#;display_errors\ =\ Off#display_errors\ =\ Off#g' /etc/php/8.3/apache2/php.ini
sed -i 's#output_buffering\ =\ 4096#output_buffering\ =\ Off#g' /etc/php/8.3/apache2/php.ini

sed -i 's#;zend_extension=opcache#zend_extension=opcache#g' /etc/php/8.3/apache2/php.ini
sed -i '/zend_extension=opcache/a opcache.enable = 1\
opcache.interned_strings_buffer = 8\
opcache.max_accelerated_files = 10000\
opcache.memory_consumption = 128\
opcache.save_comments = 1\
opcache.revalidate_freq = 1' /etc/php/8.3/apache2/php.ini

systemctl restart apache2

# Install MariaDB
apt-get install mariadb-server -y
systemctl enable --now mariadb

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

mysql -uroot -p'rootDBpass' -e "create database nextcloud_db character set utf8mb4 collate utf8mb4_bin;"
mysql -uroot -p'rootDBpass' -e "create user 'nextclouduser'@'localhost' identified by 'nextcloudpass';"
mysql -uroot -p'rootDBpass' -e "grant all privileges on nextcloud_db.* to nextclouduser@localhost identified by 'nextcloudpass';"
# mysql -uroot -p'rootDBpass' -e "show grants for nextclouduser@localhost;"

apt-get install curl unzip -y
curl -o /var/www/nextcloud.zip https://download.nextcloud.com/server/releases/latest.zip
unzip /var/www/nextcloud.zip -d /var/www/html/
chown -R www-data:www-data /var/www/html/nextcloud

echo 'ServerName $(hostname)' >> /etc/apache2/conf-available/fqdn.conf

echo "
<VirtualHost *:80>
    ServerName 127.0.0.1
 
    DocumentRoot "/var/www/html/nextcloud"
    <Directory "/var/www/html/nextcloud">
            Require all granted
            AllowOverride All
            Options FollowSymLinks MultiViews
    
            <IfModule mod_dav.c>
                Dav off
            </IfModule>
    
            SetEnv HOME /var/www/html/nextcloud
            SetEnv HTTP_HOME /var/www/html/nextcloud
    </Directory>
</VirtualHost>" >> /etc/apache2/sites-available/nextcloud.conf

a2ensite nextcloud.conf
a2dissite 000-default.conf
apachectl configtest
systemctl reload apache2
systemctl restart apache2

# reset password
# sudo -u www-data php /var/www/html/nextcloud/occ user:resetpassword admin
# reset nombre de requetes
# sudo -u www-data php /var/www/html/nextcloud/occ security:bruteforce:reset <ipaddress>

# apt install certbot python3-certbot-apache -y
# certbot --apache --agree-tos --redirect --hsts --staple-ocsp --email user@hwdomain.io -d nextcloud.hwdomain.io