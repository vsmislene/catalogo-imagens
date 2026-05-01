import os
import io
import re
import json
import unicodedata
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

FOLDER_ID = "1gHH_jC3MiCpyJjtXGki4vDkzYDhLroj0"
DEST_FOLDER = "images"
MAP_FILE = "images_map.json"

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
    fields="files(id, name, mimeType)",
    pageSize=1000
).execute()

files = results.get("files", [])

os.makedirs(DEST_FOLDER, exist_ok=True)

mapa_imagens = {}

for file in files:
    mime = file.get("mimeType", "")

    if not mime.startswith("image/"):
        print(f"Ignorado: {file['name']}")
        continue

    file_id = file["id"]
    nome_original = file["name"]

    nome_final = slugify_filename(nome_original)
    filepath = os.path.join(DEST_FOLDER, nome_final)

    request = service.files().get_media(fileId=file_id)

    with io.FileIO(filepath, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False

        while not done:
            _, done = downloader.next_chunk()

    nome_sem_ext = os.path.splitext(nome_final)[0]
    mapa_imagens[nome_sem_ext] = nome_final

    print(f"Baixado: {filepath}")

with open(MAP_FILE, "w", encoding="utf-8") as f:
    json.dump(mapa_imagens, f, ensure_ascii=False, indent=2, sort_keys=True)

print(f"{MAP_FILE} gerado com {len(mapa_imagens)} imagens.")
