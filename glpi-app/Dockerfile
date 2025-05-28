###############################################################################
# GLPI 10.0.18 ▸ PHP-FPM 8.2 + Debian + Nginx + Supervisor
###############################################################################
FROM php:8.2-fpm               

############################
# 1. Dependencias de sistema
############################
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      nginx supervisor curl git bash \
      libpng-dev libjpeg-dev libwebp-dev libfreetype6-dev \
      libxml2-dev libicu-dev libzip-dev \
      libonig-dev libldap2-dev libbz2-dev libcurl4-openssl-dev \
      default-libmysqlclient-dev pkg-config \
      && rm -rf /var/lib/apt/lists/*

############################
# 2. Extensiones de PHP
############################
RUN docker-php-ext-configure gd --with-freetype --with-jpeg --with-webp \
 && docker-php-ext-configure mysqli --with-mysqli=mysqlnd \
 && docker-php-ext-install -j"$(nproc)" \
      mysqli pdo_mysql intl xml gd mbstring zip opcache curl exif ldap bz2

############################
# 3. PHP-FPM configuración mínima
############################
RUN { \
      echo "daemonize = no"; \
      echo "include = /usr/local/etc/php-fpm.d/*.conf"; \
      echo "error_log = /usr/local/var/log/php-fpm.log"; \
    } > /usr/local/etc/php-fpm.conf \
 && mkdir -p /usr/local/var/log /usr/local/etc/php-fpm.d \
 && printf "[www]\nlisten = 9000\nuser = www-data\ngroup = www-data\npm = dynamic\n" \
      > /usr/local/etc/php-fpm.d/www.conf \
 && echo "session.cookie_httponly = On" > /usr/local/etc/php/conf.d/security.ini

############################
# 4. Descarga e instalación de GLPI
############################
ENV GLPI_VERSION=10.0.18
RUN mkdir -p /var/www/html/glpi \
 && curl -L "https://github.com/glpi-project/glpi/releases/download/${GLPI_VERSION}/glpi-${GLPI_VERSION}.tgz" \
      -o glpi.tgz \
 && tar -xzf glpi.tgz -C /var/www/html/glpi --strip-components=1 \
 && rm glpi.tgz

############################
# 5. Permisos
############################
RUN chown -R www-data:www-data /var/www/html/glpi \
 && chmod -R 775 /var/www/html/glpi/files /var/www/html/glpi/config

############################
# 6. Copiar configuraciones
############################
COPY supervisord.conf /etc/supervisord.conf
COPY glpi.ini         /etc/supervisor.d/glpi.ini
COPY glpi.conf        /etc/nginx/sites-enabled/default

############################
# 7. Exponer y arrancar
############################
EXPOSE 80
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
