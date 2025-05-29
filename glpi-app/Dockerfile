###############################################################################
# GLPI 10.0.18 ▸ Ubuntu 22.04 | PHP-FPM 8.2 | Nginx | Supervisor
###############################################################################
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC \
    GLPI_VERSION=10.0.18

###############################################################################
# 1. Paquetes de sistema + PPA Ondřej
###############################################################################
RUN apt-get update && \
    #añadimos gnupg y software-properties-common
    apt-get install -y --no-install-recommends \
        gnupg curl ca-certificates lsb-release software-properties-common && \
    add-apt-repository -y ppa:ondrej/php   && \
    add-apt-repository -y ppa:ondrej/nginx && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        supervisor nginx-full unzip wget git \
        php8.2-fpm php8.2-cli php8.2-mysql \
        php8.2-intl php8.2-xml php8.2-gd php8.2-mbstring php8.2-zip \
        php8.2-curl php8.2-bz2 php8.2-ldap php8.2-exif php8.2-opcache && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
    # Creamos el archivo con las directivas de seguridad
RUN printf "session.cookie_httponly = 1\nsession.cookie_secure = 1\n" \
      > /etc/php/8.2/fpm/conf.d/90-security.ini                 ### ← añadido

###############################################################################
# 2 ▪︎ PHP-FPM – configuración mínima (sin CR/LF ni BOM)
###############################################################################
RUN mkdir -p /run/php
RUN cat >/etc/php/8.2/fpm/php-fpm.conf <<'EOF'
[global]
pid        = /run/php/php-fpm.pid
error_log  = /proc/self/fd/2          ; logs a STDERR
include    = /etc/php/8.2/fpm/pool.d/*.conf
EOF

RUN cat >/etc/php/8.2/fpm/pool.d/www.conf <<'EOF'
[www]
user  = www-data
group = www-data
listen = 9000
pm = dynamic
pm.max_children   = 10
pm.start_servers  = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
catch_workers_output = yes
EOF

###############################################################################
# 3 ▪︎ Nginx – eliminar sitio por defecto y usar tu vhost GLPI
###############################################################################
RUN rm -r /etc/nginx/sites-enabled/default
# tu glpi.conf se copiará a /etc/nginx/conf.d/ por la instrucción COPY más abajo

# directorios que nginx necesita escribir
RUN mkdir -p /var/lib/nginx/body && chown -R www-data:www-data /var/lib/nginx

###############################################################################
# 4 ▪︎ Descargar e instalar GLPI
###############################################################################
RUN mkdir -p /var/www/html/glpi && \
    wget -q https://github.com/glpi-project/glpi/releases/download/${GLPI_VERSION}/glpi-${GLPI_VERSION}.tgz -O /tmp/glpi.tgz && \
    tar -xzf /tmp/glpi.tgz -C /var/www/html/glpi --strip-components=1 && \
    rm /tmp/glpi.tgz && \
    chown -R www-data:www-data /var/www/html/glpi && \
    chown -R www-data:www-data /var/www/html/glpi/public && \
    chmod -R 755 /var/www/html/glpi && \
    chmod -R 775 /var/www/html/glpi/files /var/www/html/glpi/config /var/www/html/glpi/marketplace /var/www/html/glpi/plugins && \
    chown -R www-data:www-data /var/www/html/glpi && \
    chmod -R 755 /var/www/html/glpi
    #rm -f /var/www/html/glpi/install/install.php && \    
    #chown -R www-data:www-data /var/www/html/glpi

###############################################################################
# 5 ▪︎ Copiar configuraciones  (👇 estas son tus archivos existentes)
###############################################################################
#RUN mkdir -p /run/php
COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY glpi.ini         /etc/supervisor/conf.d/glpi.ini
COPY glpi.conf        /etc/nginx/conf.d/glpi.conf

###############################################################################
# 6 ▪︎ Exponer puerto 80 y arrancar Supervisor con su conf explícita
###############################################################################
EXPOSE 80
CMD ["/usr/bin/supervisord","-c","/etc/supervisor/supervisord.conf"]
