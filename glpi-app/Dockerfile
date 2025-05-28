# ──────────────────────────────────────────────
# GLPI 10.0.18 con PHP 8.2 + Alpine + Nginx + Supervisor
# ──────────────────────────────────────────────

FROM php:8.2-fpm-alpine

# ──────────────────────────────────────────────
# 1. Instalación de dependencias
# ──────────────────────────────────────────────
RUN apk add --no-cache --virtual .build-deps \
        $PHPIZE_DEPS \
    && apk add --no-cache \
        nginx supervisor curl bash git \
        libpng libpng-dev libxml2-dev oniguruma-dev icu-dev libzip-dev \
    && docker-php-ext-install -j$(nproc) pdo_mysql intl xml gd mbstring zip opcache \
    && apk del .build-deps

# ──────────────────────────────────────────────
# 2. Configuración mínima de PHP-FPM
# ──────────────────────────────────────────────
RUN mkdir -p /usr/local/etc/php-fpm.d \
 && echo "[global]\ndaemonize = no" > /usr/local/etc/php-fpm.conf \
 && echo "[www]\nlisten = 9000\nuser = www-data\ngroup = www-data\npm = dynamic\npm.max_children = 5\npm.start_servers = 2\npm.min_spare_servers = 1\npm.max_spare_servers = 3" > /usr/local/etc/php-fpm.d/www.conf \
 && mkdir -p /usr/local/var/log \
 && touch /usr/local/var/log/php-fpm.log \
 && chown -R www-data:www-data /usr/local/var/log/php-fpm.log

# ──────────────────────────────────────────────
# 3. Descarga e instalación de GLPI
# ──────────────────────────────────────────────
ENV GLPI_VERSION=10.0.18
RUN mkdir -p /var/www/html/glpi \
 && curl -L https://github.com/glpi-project/glpi/releases/download/${GLPI_VERSION}/glpi-${GLPI_VERSION}.tgz -o glpi.tgz \
 && tar -xzf glpi.tgz -C /var/www/html/glpi --strip-components=1 \
 && rm glpi.tgz \
 && chown -R www-data:www-data /var/www/html/glpi

# ──────────────────────────────────────────────
# 4. Configuración de Supervisor y Nginx
# ──────────────────────────────────────────────
COPY supervisord.conf /etc/supervisord.conf
COPY glpi.ini /etc/supervisor.d/glpi.ini
COPY glpi.conf /etc/nginx/http.d/default.conf

# ──────────────────────────────────────────────
# 5. Exposición del puerto y arranque
# ──────────────────────────────────────────────
EXPOSE 80
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]