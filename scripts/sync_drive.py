import os
import io
import re
import unicodedata
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

FOLDER_ID = "1gHH_jC3MiCpyJjtXGki4vDkzYDhLroj0"
DEST_FOLDER = "images"

def slugify_filename(filename):
    name, ext = os.path.splitext(filename)
    ext = ext.lower()

    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = name.strip("-")

    return f"{name}{ext}"

creds = service_account.Credentials.from_service_account_file(
    "service-account.json",
    scopes=["https://www.googleapis.com/auth/drive.readonly"]
)

service = build("drive", "v3", credentials=creds)

query = f"'{FOLDER_ID}' in parents and trashed = false"

results = service.files().list(
    q=query,
    fields="files(id, name, mimeType)"
).execute()

files = results.get("files", [])

os.makedirs(DEST_FOLDER, exist_ok=True)

for file in files:
    mime = file.get("mimeType", "")

    if not mime.startswith("image/"):
        print(f"Ignorado: {file['name']}")
        continue

    file_id = file["id"]
    filename = slugify_filename(file["name"])
    filepath = os.path.join(DEST_FOLDER, filename)

    request = service.files().get_media(fileId=file_id)

    with io.FileIO(filepath, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

    print(f"Baixado: {filepath}")

import json

mapa_imagens = {}

for file in files:
    mime = file.get("mimeType", "")

    if not mime.startswith("image/"):
        continue

    nome_original = file["name"]
    nome_final = gerar_nome(nome_original)

    nome_sem_ext = os.path.splitext(nome_final)[0]

    mapa_imagens[nome_sem_ext] = nome_final

# salva o JSON
with open("images_map.json", "w") as f:
    json.dump(mapa_imagens, f)
