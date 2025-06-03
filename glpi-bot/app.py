#!/usr/bin/env python3
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import requests

# --------------------------------------------------------------
# 1) Variables de entorno necesarias
# --------------------------------------------------------------
# URL base de la API REST de GLPI (desde el contenedor "glpi-app")
# Por defecto apunta a http://glpi-app/apirest.php, pero puedes revisarlo en tu docker-compose.
GLPI_URL = os.getenv("GLPI_URL", "http://glpi-app/apirest.php")

# App-Token y User-Token deben estar definidos en tu .env o en docker-compose.yml
GLPI_APP_TOKEN  = os.getenv("GLPI_APP_TOKEN")
GLPI_USER_TOKEN = os.getenv("GLPI_USER_TOKEN")

# Puerto en el que este servidor escuchará (coincide con PORT en docker-compose)
PORT = int(os.getenv("PORT", "8000"))

# --------------------------------------------------------------
# 2) Handler simple para el endpoint /ticket
# --------------------------------------------------------------
class TicketHandler(BaseHTTPRequestHandler):
    def _send_json(self, code, payload):
        """
        Envía una respuesta JSON con el status code indicado.
        """
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_POST(self):
        # Sólo aceptamos POST a la ruta "/ticket"
        if self.path != "/ticket":
            self._send_json(404, {"detail": "Not Found"})
            return

        # Leer el body
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)

        # Intentar parsear JSON
        try:
            data = json.loads(raw_body)
        except json.JSONDecodeError:
            self._send_json(400, {"detail": "JSON inválido"})
            return

        # Obtener "title" y "content"
        title = data.get("title")
        content = data.get("content")
        if not title or not content:
            self._send_json(400, {"detail": "'title' y 'content' son obligatorios"})
            return

        # ----------------------------------------------------------
        # 3) Llamada a la API REST de GLPI para crear el ticket
        # ----------------------------------------------------------
        headers = {
            "App-Token":     GLPI_APP_TOKEN,
            "User-Token": GLPI_USER_TOKEN,
            "Content-Type":  "application/json"
        }
        payload = {
            "input": {
                "name":    title,
                "content": content
            }
        }
        try:
            resp = requests.post(f"{GLPI_URL}/Ticket", headers=headers, json=payload)
        except Exception as e:
            # Si la petición HTTP falla (ej. no se conecta), devolvemos 500
            self._send_json(500, {"detail": f"Error al conectar con GLPI: {str(e)}"})
            return

        # Si GLPI devolvió 201, parseamos el ID del ticket
        if resp.status_code == 201:
            try:
                ticket_id = resp.json().get("id")
            except ValueError:
                # Si la respuesta de GLPI no es JSON
                ticket_id = None

            return self._send_json(201, {"ticket_id": ticket_id})

        # Si GLPI devolvió otro código, devolvemos ese mismo código y el texto de error
        try:
            detalle_error = resp.json()
        except ValueError:
            detalle_error = resp.text

        self._send_json(resp.status_code, {"detail": detalle_error})

    # Opcional: podemos ignorar cualquier GET (devolver 404)
    def do_GET(self):
        self._send_json(404, {"detail": "Only POST allowed"})


# --------------------------------------------------------------
# 4) Función principal para arrancar el servidor
# --------------------------------------------------------------
def run():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, TicketHandler)
    print(f"[+] Servidor HTTP escuchando en el puerto {PORT}", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[-] Servidor detenido manualmente", flush=True)
        httpd.server_close()


if __name__ == "__main__":
    # Validar que estén definidas las variables de entorno mínimas
    missing = []
    if not GLPI_APP_TOKEN:
        missing.append("GLPI_APP_TOKEN")
    if not GLPI_USER_TOKEN:
        missing.append("GLPI_USER_TOKEN")
    if missing:
        print(f"[!] ERROR: faltan variables de entorno: {', '.join(missing)}")
        print("    Asegúrate de definirlas en tu docker-compose.yml o .env antes de correr este contenedor.")
        exit(1)

    run()
