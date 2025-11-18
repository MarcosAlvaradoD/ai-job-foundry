# send_test_email.py
import os, base64, time
from email.message import EmailMessage

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ---------------- CONFIG ----------------
ME = "markalvati@gmail.com"       # tu correo (remitente y destinatario)
LABEL_PATH = "JOBS/Inbound"       # crea JOBS y subetiqueta Inbound si no existen
SUBJECT = f"[JobsTest] Recruiter ping {time.strftime('%F %T')}"
BODY = "Hola Mark,\n\nEste es un correo de PRUEBA para el pipeline. \n\n– Bot"
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels",
]

def need_new_consent(existing_creds: Credentials) -> bool:
    if not existing_creds or not existing_creds.valid:
        return True
    have = set(existing_creds.scopes or [])
    want = set(SCOPES)
    return not want.issubset(have)

def get_service():
    if not os.path.exists("credentials.json"):
        raise FileNotFoundError("Falta credentials.json junto al script (OAuth de escritorio).")
    creds = None
    if os.path.exists("token.json"):
        try:
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        except Exception:
            creds = None
    if need_new_consent(creds):
        # Fuerza nuevo login con los scopes correctos
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json","w") as f:
            f.write(creds.to_json())
    return build("gmail","v1",credentials=creds)

def ensure_label(service, full_name):
    # Soporta nesting "PARENT/CHILD"
    parts = full_name.split("/")
    parent = None
    current_name = ""
    # cache de labels para no llamar list() en cada vuelta
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    def find_label(name):
        return next((L for L in labels if L.get("name")==name), None)

    for p in parts:
        current_name = p if parent is None else f"{parent['name']}/{p}"
        found = find_label(current_name)
        if not found:
            body = {
                "name": current_name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show"
            }
            found = service.users().labels().create(userId="me", body=body).execute()
            labels.append(found)  # actualizar cache
        parent = found
    return parent["id"]

def send_and_label():
    svc = get_service()
    # 1) asegurar label
    label_id = ensure_label(svc, LABEL_PATH)

    # 2) construir el MIME
    msg = EmailMessage()
    msg["To"] = ME
    msg["From"] = ME
    msg["Subject"] = SUBJECT
    msg.set_content(BODY)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")

    # 3) enviar
    sent = svc.users().messages().send(userId="me", body={"raw": raw}).execute()
    mid = sent["id"]

    # 4) aplicar label (y opcionalmente quitar INBOX)
    svc.users().messages().modify(
        userId="me",
        id=mid,
        body={"addLabelIds":[label_id]}  # "removeLabelIds":["INBOX"] si quieres sacarlo de la Bandeja
    ).execute()

    print("OK -> enviado y etiquetado:", mid, "| label:", LABEL_PATH)

if __name__ == "__main__":
    send_and_label()
