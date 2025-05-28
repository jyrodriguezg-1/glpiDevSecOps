###############################################################################
# GLPI 10.0.18 ▸ PHP-FPM 8.2 + Ubuntu 22.04 + Nginx + Supervisor
###############################################################################
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /var/www/html

###############################################################################
# 1 ▸ Habilitar el PPA de Ondřej Surý (PHP 8.2) y evitar HTTP 418
###############################################################################
RUN apt-get update && apt-get install -y --no-install-recommends \
        software-properties-common gnupg2 ca-certificates curl lsb-release \
 && add-apt-repository ppa:ondrej/php -y \
 && echo 'Acquire::https::packages.sury.org::User-Agent "Mozilla/5.0";' \
      > /etc/apt/apt.conf.d/90suryUA

###############################################################################
# 2 ▸ Paquetes de sistema + PHP 8.2 con extensiones que exige GLPI
###############################################################################
RUN apt-get update && apt-get install -y --no-install-recommends \
      nginx supervisor git wget unzip \
      php8.2-fpm php8.2-cli \
      php8.2-mysql php8.2-mysqli php8.2-intl php8.2-xml php8.2-gd \
      php8.2-mbstring php8.2-zip php8.2-curl php8.2-bz2 php8.2-ldap \
      php8.2-exif php8.2-opcache \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

 ###############################################################################
# 2 bis ▸ Garantizar que Nginx pueda crear su PID y los cuerpos de subida
###############################################################################
RUN mkdir -p /run /var/lib/nginx/body \
 && chown -R root:root /run /var/lib/nginx

############################
# 3 ▸ PHP-FPM – config mínima limpia
############################
RUN printf '%s\n' \
'[global]' \
'daemonize = no' \
'include = /etc/php/8.2/fpm/pool.d/*.conf' \
'error_log = /proc/self/fd/2' \
> /etc/php/8.2/fpm/php-fpm.conf && \
printf '%s\n' \
'[www]' \
'listen = 9000' \
'user = www-data' \
'group = www-data' \
'pm = dynamic' \
> /etc/php/8.2/fpm/pool.d/www.conf


###############################################################################
# 4 ▸ Descargar e instalar GLPI
###############################################################################
ENV GLPI_VERSION=10.0.18
RUN mkdir -p /var/www/html/glpi \
 && curl -L "https://github.com/glpi-project/glpi/releases/download/${GLPI_VERSION}/glpi-${GLPI_VERSION}.tgz" \
      -o /tmp/glpi.tgz \
 && tar -xzf /tmp/glpi.tgz -C /var/www/html/glpi --strip-components=1 \
 && rm /tmp/glpi.tgz

###############################################################################
# 5 ▸ Permisos de GLPI y paths que necesita Nginx
###############################################################################
RUN chown -R www-data:www-data /var/www/html/glpi \
 && chmod -R 775 /var/www/html/glpi/files /var/www/html/glpi/config \
 && mkdir -p /var/lib/nginx/body \
 && chown -R www-data:www-data /var/lib/nginx

###############################################################################
# 6 ▸ Config. de Nginx y Supervisor
###############################################################################
COPY glpi.conf        /etc/nginx/sites-enabled/default
COPY supervisord.conf /etc/supervisord.conf
COPY glpi.ini         /etc/supervisor/conf.d/glpi.ini

###############################################################################
# 7 ▸ Exponer puerto 80 y lanzar Supervisor
###############################################################################
EXPOSE 80
CMD ["/usr/bin/supervisord","-c","/etc/supervisord.conf"]
