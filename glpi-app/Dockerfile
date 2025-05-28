###############################################################################
# GLPI 10.0.18  ▸  PHP-FPM 8.2 + Alpine + Nginx + Supervisor
###############################################################################
FROM php:8.2-fpm-alpine

############################
# 1. Dependencias del sistema
############################
RUN apk add --no-cache --virtual .build-deps \
        $PHPIZE_DEPS \
    && apk add --no-cache \
        nginx supervisor curl bash git \
        libpng libpng-dev libxml2-dev oniguruma-dev icu-dev libzip-dev \
    && docker-php-ext-install -j"$(nproc)" pdo_mysql intl xml gd mbstring zip opcache \
    && apk del .build-deps

############################
# 2. PHP-FPM – config mínima
############################
# ───────── bloque PHP-FPM corregido ─────────
RUN printf "daemonize = no\ninclude = /usr/local/etc/php-fpm.d/*.conf\n" \
           "error_log = /usr/local/var/log/php-fpm.log\n" \ 
        > /usr/local/etc/php-fpm.conf \
 && mkdir -p /usr/local/etc/php-fpm.d \
 && printf "[www]\nlisten = 9000\nuser = www-data\ngroup = www-data\npm = dynamic\npm.max_children = 5\npm.start_servers = 2\npm.min_spare_servers = 1\npm.max_spare_servers = 3\n" \
        > /usr/local/etc/php-fpm.d/www.conf \
 && mkdir -p /usr/local/var/log \
 && touch /usr/local/var/log/php-fpm.log \
 && chown -R www-data:www-data /usr/local/var/log/php-fpm.log


############################
# 3. GLPI – descarga y despliegue
############################
ENV GLPI_VERSION=10.0.18
RUN mkdir -p /var/www/html/glpi \
 && curl -L "https://github.com/glpi-project/glpi/releases/download/${GLPI_VERSION}/glpi-${GLPI_VERSION}.tgz" -o glpi.tgz \
 && tar -xzf glpi.tgz -C /var/www/html/glpi --strip-components=1 \
 && rm glpi.tgz \
 && chown -R www-data:www-data /var/www/html/glpi

############################
# 4. Copia de configuraciones
############################
COPY supervisord.conf      /etc/supervisord.conf
COPY glpi.ini              /etc/supervisor.d/glpi.ini
COPY glpi.conf             /etc/nginx/http.d/default.conf   
# único archivo de Nginx

############################
# 5. Exponer puerto y arrancar
############################
EXPOSE 80
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
