###############################################################################
# GLPI 10.0.18 ▸ PHP-FPM 8.2 + Alpine + Nginx + Supervisor                    #
###############################################################################
FROM php:8.2-fpm-alpine

############################
# 1. Dependencias de sistema
############################
RUN apk add --no-cache --virtual .build-deps \
        $PHPIZE_DEPS \
    && apk add --no-cache \
        nginx supervisor curl bash git \
        libpng libpng-dev libxml2-dev oniguruma-dev icu-dev libzip-dev \
        openldap-dev bzip2-dev mariadb-dev \          
        # ← AÑADIDO mariadb-dev
        # libs extra por si quieres futuras extensiones
        libjpeg-turbo-dev libwebp-dev freetype-dev

############################
# 2. Extensiones de PHP
############################
# Compilamos mysqli con mysqlnd y el resto de módulos que pide GLPI
RUN docker-php-ext-configure mysqli --with-mysqli=mysqlnd \
 && docker-php-ext-install -j"$(nproc)" \
      pdo_mysql mysqli intl xml gd mbstring zip opcache curl \
      exif ldap bz2

############################
# 3. PHP-FPM (config mínima)
############################
RUN printf 'daemonize = no\n' \
          'include = /usr/local/etc/php-fpm.d/*.conf\n' \
          'error_log = /usr/local/var/log/php-fpm.log\n' \
          > /usr/local/etc/php-fpm.conf \
 && mkdir -p /usr/local/etc/php-fpm.d \
 && printf '[www]\nlisten = 9000\nuser = root\ngroup = root\npm = dynamic\n' \
          > /usr/local/etc/php-fpm.d/www.conf \
 && mkdir -p /usr/local/var/log \
 && touch /usr/local/var/log/php-fpm.log

# Directiva de seguridad (cookie httponly)
RUN echo 'session.cookie_httponly = On' > /usr/local/etc/php/conf.d/security.ini

############################
# 4. Descarga e instalación de GLPI
############################
ENV GLPI_VERSION=10.0.18
RUN mkdir -p /var/www/html/glpi \
 && curl -L "https://github.com/glpi-project/glpi/releases/download/${GLPI_VERSION}/glpi-${GLPI_VERSION}.tgz" -o glpi.tgz \
 && tar -xzf glpi.tgz -C /var/www/html/glpi --strip-components=1 \
 && rm glpi.tgz

# (Opcional) mover datos fuera del doc-root
# RUN mv /var/www/html/glpi/files /var/lib/glpi

############################
# 5. Permisos
############################
RUN chown -R root:root /var/www/html/glpi \
 && chmod -R 775 /var/www/html/glpi/files /var/www/html/glpi/config

############################
# 6. Copia de configuraciones
############################
COPY supervisord.conf /etc/supervisord.conf
COPY glpi.ini         /etc/supervisor.d/glpi.ini
COPY glpi.conf        /etc/nginx/http.d/default.conf

############################
# 7. Exponer puerto y arrancar
############################
EXPOSE 80
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
