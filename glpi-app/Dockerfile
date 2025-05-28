###############################################################################
# GLPI 10.0.18 ▸ PHP-FPM 8.2 + Ubuntu 22.04 + Nginx + Supervisor
###############################################################################
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

###############################################################################
# 1. Añadir el PPA de Sury para obtener PHP 8.2 en Ubuntu
###############################################################################
RUN apt-get update && apt-get install -y --no-install-recommends \
        gnupg2 ca-certificates curl lsb-release \
 && curl -fsSL https://packages.sury.org/php/apt.gpg | gpg --dearmor -o /etc/apt/trusted.gpg.d/sury-php.gpg \
 && echo "deb https://packages.sury.org/php $(lsb_release -sc) main" \
      > /etc/apt/sources.list.d/sury-php.list

###############################################################################
# 2. Paquetes de sistema y PHP 8.2 + extensiones
###############################################################################
RUN apt-get update && apt-get install -y --no-install-recommends \
      nginx supervisor git wget unzip \
      php8.2-fpm php8.2-cli php8.2-mysql php8.2-mysqli \
      php8.2-intl php8.2-xml php8.2-gd php8.2-mbstring php8.2-zip \
      php8.2-curl php8.2-bz2 php8.2-ldap php8.2-exif php8.2-opcache \
      && apt-get clean && rm -rf /var/lib/apt/lists/*

############################
# 3. PHP-FPM (config mínima)
############################
RUN printf "%s\n" \
"[global]" \
"daemonize = no" \
"include = /usr/local/etc/php-fpm.d/*.conf" \
"error_log = /proc/self/fd/2" \
> /usr/local/etc/php-fpm.conf

# Ajustamos el pool www (sobrescribimos el que viene por defecto)
RUN cat > /etc/php/8.2/fpm/pool.d/www.conf <<'EOF'
[www]
listen = 9000
user  = www-data
group = www-data
pm = dynamic
pm.max_children = 10
pm.start_servers = 4
pm.min_spare_servers = 2
pm.max_spare_servers = 6
access.log = /proc/self/fd/2
clear_env = no
EOF

# Endurecer cookies de sesión
RUN echo "session.cookie_httponly = On" > /etc/php/8.2/fpm/conf.d/99-security.ini

###############################################################################
# 4. Descargar e instalar GLPI
###############################################################################
ENV GLPI_VERSION=10.0.18
RUN mkdir -p /var/www/html/glpi \
 && curl -L "https://github.com/glpi-project/glpi/releases/download/${GLPI_VERSION}/glpi-${GLPI_VERSION}.tgz" \
      -o /tmp/glpi.tgz \
 && tar -xzf /tmp/glpi.tgz -C /var/www/html/glpi --strip-components=1 \
 && rm /tmp/glpi.tgz

###############################################################################
# 5. Permisos (www-data)
###############################################################################
RUN chown -R www-data:www-data /var/www/html/glpi \
 && chmod -R 775 /var/www/html/glpi/files /var/www/html/glpi/config

###############################################################################
# 6. Copiar configuraciones de Nginx y Supervisor
###############################################################################
COPY glpi.conf        /etc/nginx/sites-enabled/default
COPY supervisord.conf /etc/supervisord.conf
COPY glpi.ini         /etc/supervisor/conf.d/glpi.ini

###############################################################################
# 7. Exponer puerto y CMD
###############################################################################
EXPOSE 80
CMD ["/usr/bin/supervisord","-c","/etc/supervisord.conf"]
