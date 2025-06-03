# glpi-app/Dockerfile
###############################################################################
# GLPI 10.0.18 ▸ Ubuntu 22.04 | PHP-FPM 8.2 | Nginx | Supervisor
###############################################################################
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC \
    GLPI_VERSION=10.0.18

###############################################################################
# 1) Instalamos transport HTTPS y herramientas básicas
###############################################################################
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      apt-transport-https \
      ca-certificates \
      gnupg \
      lsb-release \
      software-properties-common \
      curl \
      wget \
 && rm -rf /var/lib/apt/lists/*

###############################################################################
# 2) Añadimos los PPA de Ondřej para PHP y Nginx
###############################################################################
RUN add-apt-repository -y ppa:ondrej/php \
 && add-apt-repository -y ppa:ondrej/nginx

###############################################################################
# 3) Instalamos Nginx, PHP-FPM, Supervisor y utilidades
###############################################################################
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      nginx-full \
      supervisor \
      unzip \
      git \
      vim \
      php8.2-fpm \
      php8.2-cli \
      php8.2-mysql \
      php8.2-intl \
      php8.2-xml \
      php8.2-gd \
      php8.2-mbstring \
      php8.2-zip \
      php8.2-curl \
      php8.2-bz2 \
      php8.2-ldap \
      php8.2-exif \
      php8.2-opcache \
 && rm -rf /var/lib/apt/lists/*

# Ajuste de seguridad de sesiones (HTTPS=0 para HTTP)
RUN printf "session.cookie_httponly = 1\nsession.cookie_secure = 0\n" \
      > /etc/php/8.2/fpm/conf.d/90-security.ini

###############################################################################
# 4) Configuración embebida de PHP-FPM
###############################################################################
RUN mkdir -p /run/php \
 && cat >/etc/php/8.2/fpm/php-fpm.conf <<'EOF'
[global]
pid        = /run/php/php-fpm.pid
error_log  = /proc/self/fd/2
include    = /etc/php/8.2/fpm/pool.d/*.conf
EOF

RUN cat >/etc/php/8.2/fpm/pool.d/www.conf <<'EOF'
[www]
user            = www-data
group           = www-data
listen          = 9000
pm              = dynamic
pm.max_children = 10
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
catch_workers_output = yes
EOF

###############################################################################
# 5) Preparamos Nginx
###############################################################################
RUN rm -f /etc/nginx/sites-enabled/default \
 && mkdir -p /var/lib/nginx/body \
 && chown -R www-data:www-data /var/lib/nginx

###############################################################################
# 6) Descargamos e instalamos GLPI
###############################################################################
COPY glpi-10.0.18.tgz /tmp/glpi.tgz

RUN mkdir -p /var/www/html/glpi \
 && tar -xzf /tmp/glpi.tgz -C /var/www/html/glpi --strip-components=1 \
 && rm /tmp/glpi.tgz \
 && chown -R www-data:www-data /var/www/html/glpi/files /var/www/html/glpi/config /var/www/html/glpi/marketplace /var/www/html/glpi/plugins \
 && find /var/www/html/glpi -type d -exec chmod 775 {} + \
 && find /var/www/html/glpi -type f -exec chmod 644 {} +

# RUN mkdir -p /var/www/html/glpi \
#  && wget -q https://github.com/glpi-project/glpi/releases/download/${GLPI_VERSION}/glpi-${GLPI_VERSION}.tgz \
#        -O /tmp/glpi.tgz \
#  && tar -xzf /tmp/glpi.tgz -C /var/www/html/glpi --strip-components=1 \
#  && rm /tmp/glpi.tgz \
#  && chown -R www-data:www-data /var/www/html/glpi \
#  && find /var/www/html/glpi/files /var/www/html/glpi/config /var/www/html/glpi/marketplace /var/www/html/glpi/plugins \
#        -type d -exec chmod 775 {} + \
#  && find /var/www/html/glpi -type f -exec chmod 644 {} +
###############################################################################
# 7) Copiamos supervisord, ini y glpi.conf corregido
###############################################################################
COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY glpi.ini         /etc/supervisor/conf.d/glpi.ini
COPY glpi.conf        /etc/nginx/conf.d/glpi.conf

RUN rm -f /etc/nginx/conf.d/default.conf \
 && mkdir -p /var/lib/php/sessions \
 && chown -R www-data:www-data /var/lib/php/sessions \
 && chmod 770 /var/lib/php/sessions

EXPOSE 80
CMD ["/usr/bin/supervisord","-c","/etc/supervisor/supervisord.conf"]
