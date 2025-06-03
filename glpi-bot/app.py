#!/usr/bin/env python3
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import requests

# --------------------------------------------------------------
# 1) Variables de entorno necesarias
# --------------------------------------------------------------
# URL base de la API REST de GLPI (contiene /apirest.php)
GLPI_URL = os.getenv("GLPI_URL", "http://glpi-app/apirest.php")

# App-Token fijo (creado en la UI de GLPI)
GLPI_APP_TOKEN = os.getenv("GLPI_APP_TOKEN")
# Login y password de un usuario válido en GLPI (para initSession)
GLPI_USER_LOGIN = os.getenv("GLPI_USER_LOGIN")
GLPI_USER_PASSWORD = os.getenv("GLPI_USER_PASSWORD")

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

        # Leer el body del cliente
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)

        # Intentar parsear JSON
        try:
            data = json.loads(raw_body)
        except json.JSONDecodeError:
            self._send_json(400, {"detail": "JSON inválido"})
            return

        # Obtener "title" y "content" del JSON
        title = data.get("title")
        content = data.get("content")
        if not title or not content:
            self._send_json(400, {"detail": "'title' y 'content' son obligatorios"})
            return

        # ----------------------------------------------------------
        # 3) Llamada a /initSession para obtener session_token
        # ----------------------------------------------------------
        init_url = f"{GLPI_URL}/initSession"
        init_headers = {
            "App-Token":     GLPI_APP_TOKEN,
            "Content-Type":  "application/json"
        }
        init_payload = {
            "login":    GLPI_USER_LOGIN,
            "password": GLPI_USER_PASSWORD
        }

        try:
            init_resp = requests.post(init_url, headers=init_headers, json=init_payload, timeout=10)
        except Exception as e:
            # Si la petición a initSession falla por conexión u otro error
            self._send_json(500, {"detail": f"Error al conectar con GLPI /initSession: {str(e)}"})
            return

        # Si GLPI devolvió otro código diferente a 200, informamos al cliente
        if init_resp.status_code != 200:
            try:
                err = init_resp.json()
            except ValueError:
                err = init_resp.text
            self._send_json(init_resp.status_code, {"detail": err})
            return

        # Extraer el session_token de la respuesta
        try:
            session_token = init_resp.json().get("session_token")
        except (ValueError, AttributeError):
            self._send_json(500, {"detail": "Respuesta inválida de initSession"})
            return

        if not session_token:
            self._send_json(500, {"detail": "No se devolvió session_token en initSession"})
            return

        # ----------------------------------------------------------
        # 4) Llamada a la API REST de GLPI para crear el ticket
        # ----------------------------------------------------------
        ticket_headers = {
            "App-Token":     GLPI_APP_TOKEN,
            "Session-Token": session_token,
            "Content-Type":  "application/json"
        }
        ticket_payload = {
            "input": {
                "name":    title,
                "content": content
            }
        }
        try:
            resp = requests.post(f"{GLPI_URL}/Ticket", headers=ticket_headers, json=ticket_payload, timeout=10)
        except Exception as e:
            # Si la petición HTTP falla (ej. no se conecta), devolvemos 500
            self._send_json(500, {"detail": f"Error al conectar con GLPI /Ticket: {str(e)}"})
            return

        # Si GLPI devolvió 201, extraemos el ID del ticket
        if resp.status_code == 201:
            try:
                ticket_id = resp.json().get("id")
            except ValueError:
                ticket_id = None
            return self._send_json(201, {"ticket_id": ticket_id})

        # Si GLPI devolvió otro código (400, 401, 403, etc.), devolvemos ese mismo código y el detalle del error
        try:
            detalle_error = resp.json()
        except ValueError:
            detalle_error = resp.text

        self._send_json(resp.status_code, {"detail": detalle_error})

    # Para cualquier GET devolvemos 404
    def do_GET(self):
        self._send_json(404, {"detail": "Only POST allowed"})


# --------------------------------------------------------------
# 5) Función principal para arrancar el servidor
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
    if not GLPI_USER_LOGIN:
        missing.append("GLPI_USER_LOGIN")
    if not GLPI_USER_PASSWORD:
        missing.append("GLPI_USER_PASSWORD")
    if missing:
        print(f"[!] ERROR: faltan variables de entorno: {', '.join(missing)}")
        print("    Asegúrate de definirlas en tu docker-compose.yml o .env antes de correr este contenedor.")
        exit(1)

    run()
