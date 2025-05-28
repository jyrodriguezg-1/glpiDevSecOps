# README.md
# glpiDevSecOps

**GLPI 10 + MariaDB + Bot de tickets en un pipeline DevSecOps minimalista.**  
Desarrollado en contenedores Docker con despliegue automático a Google Cloud Compute Engine mediante GitHub Actions.

---

## 1️⃣ Requisitos previos

| Componente | Versión mínima | Notas |
|------------|---------------|-------|
| Docker Engine | 24.x | `docker -v` |
| Docker Compose | v2 | Incluido en Docker moderno |
| Cuenta Docker Hub | —— | Usuario **jyrodriguezg** en este ejemplo |
| Cuenta GCP | —— | Proyecto + facturación habilitada |
| VM Compute Engine | Ubuntu 22 LTS | Puerto 80 abierto |
| Git | 2.20+ | Para clonar el repo |

---

## 2️⃣ Instalación local paso a paso

```bash
git clone https://github.com/jyrodriguezg/glpiDevSecOps.git
cd glpiDevSecOps
```
# Copiar variables de entorno
```bash
cp .env.example .env
vim .env          # ← ajusta contraseñas y tokens
```
# Construir e iniciar los contenedores
```bash
docker compose up -d --build
```
# Navega en tu navegador:
# http://localhost:8080  → Instalador GLPI
# http://localhost:8000/ping → Health-check del bot

⚠️ Primer uso de GLPI:
En el instalador selecciona la BD glpi con usuario GlpiDev. Después borra el archivo install/install.php y cambia la contraseña del usuario glpi.

3️⃣ Alta de Service Account y secretos en GitHub
Crear SA

```bash
Copiar
Editar
gcloud iam service-accounts create glpi-deployer \
  --display-name=\"SA despliegue GLPI\"
Roles mínimos
```
```bash
Copiar
Editar
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=\"serviceAccount:glpi-deployer@$PROJECT_ID.iam.gserviceaccount.com\" \
  --role=roles/compute.admin
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=\"serviceAccount:glpi-deployer@$PROJECT_ID.iam.gserviceaccount.com\" \
  --role=roles/storage.admin
Clave JSON
```
```bash
Copiar
Editar
gcloud iam service-accounts keys create key.json \
  --iam-account glpi-deployer@$PROJECT_ID.iam.gserviceaccount.com
Subir a GitHub Secrets

Secret	Valor
GCP_SERVICE_ACCOUNT_KEY	Contenido de key.json
GCP_PROJECT	ID del proyecto
GCP_ZONE	p. ej. southamerica-west1-a
GCP_INSTANCE	Nombre de la VM
DOCKERHUB_USERNAME	Tu usuario
DOCKERHUB_TOKEN	Token de acceso
```
4️⃣ Creación y preparación de la VM

```bash
Copiar
Editar
gcloud compute instances create glpi-vm \
  --zone=$GCP_ZONE \
  --machine-type=e2-medium \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --tags=http-server,https-server \
  --boot-disk-size=20GB

# Abrir puerto 80 en Firewall (si la regla no existe)
gcloud compute firewall-rules create default-allow-http \
  --allow tcp:80 --target-tags=http-server --direction=INGRESS
SSH e instala Docker + Compose:

bash
Copiar
Editar
gcloud compute ssh glpi-vm --zone=$GCP_ZONE
# En la VM…
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker
sudo apt-get install docker-compose-plugin -y

# Clona el repo para el primer despliegue manual
git clone https://github.com/jyrodriguezg/glpiDevSecOps.git
cd glpiDevSecOps
cp .env.example .env             # O sube tu .env real
docker compose up -d --build
exit
```
5️⃣ Flujo del pipeline
```bash
Commit/push a main.

Job build-and-push

Construye cada imagen con tag YYYYMMDD + latest.

Login y push a Docker Hub.

Job deploy (en cadena)

Autentica en GCP (SA).

Hace git pull y docker compose pull; up -d en la VM usando gcloud compute ssh.

Sin pruebas ni linters (según requisito).
```

6️⃣ Actualización continua

```bash
Cambio de código → push → despliegue automático (≈ 2-4 min).

Rollback:

docker compose ps en la VM.

docker compose pull <servicio>:<tag_anterior>

docker compose up -d.
```

7️⃣ Notas de seguridad
```bash
Variables sensibles solo en .env y/o GitHub Secrets.

Actualiza dependencias semanalmente → Dependabot genera PRs.

Revisa mariadb:lts y php:8.2 ante CVE críticos.

Programa copias de glpi_files y glpi_db_data (ej. cron + gsutil rsync al Cloud Storage).
```

8️⃣ Referencias rápidas

```bash
Acción	Comando
Logs de bot	docker logs -f glpi-bot
Shell en MariaDB	docker exec -it glpi-db mariadb -uGlpiDev -p
Reconstruir solo GLPI	docker compose build glpi-app && docker compose up -d glpi-app
```
