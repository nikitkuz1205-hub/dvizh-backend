import json
import os
import shutil
from uuid import uuid4

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
COVERS_DIR = os.path.join(BASE_DIR, "covers")
TRACKS_FILE = os.path.join(BASE_DIR, "tracks.json")
BASE_URL = "https://dvizh-backend.onrender.com"

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(COVERS_DIR, exist_ok=True)

if not os.path.exists(TRACKS_FILE):
    with open(TRACKS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
app.mount("/covers", StaticFiles(directory=COVERS_DIR), name="covers")


def read_tracks():
    with open(TRACKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tracks(tracks):
    with open(TRACKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tracks, f, ensure_ascii=False, indent=2)


@app.get("/")
def root():
    return {"ok": True, "service": "dvizh-backend"}


@app.get("/tracks")
def get_tracks():
    return read_tracks()


@app.post("/upload")
async def upload_track(
    title: str = Form(...),
    artist: str = Form(...),
    audio: UploadFile = File(...),
    cover: UploadFile | None = File(default=None),
):
    audio_ext = os.path.splitext(audio.filename)[1].lower()
    if audio_ext not in [".mp3", ".wav", ".m4a"]:
        return {"error": "Поддерживаются только .mp3, .wav, .m4a"}

    audio_name = f"{uuid4().hex}{audio_ext}"
    audio_path = os.path.join(UPLOADS_DIR, audio_name)

    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    cover_url = "https://placehold.co/500x500/171717/FFFFFF?text=%D0%94%D0%B2%D0%B8%D0%B6"

    if cover and cover.filename:
        cover_ext = os.path.splitext(cover.filename)[1].lower()
        if cover_ext in [".jpg", ".jpeg", ".png", ".webp"]:
            cover_name = f"{uuid4().hex}{cover_ext}"
            cover_path = os.path.join(COVERS_DIR, cover_name)

            with open(cover_path, "wb") as buffer:
                shutil.copyfileobj(cover.file, buffer)

            cover_url = f"{BASE_URL}/covers/{cover_name}"

    track = {
        "title": title,
        "artist": artist,
        "cover": cover_url,
        "src": f"{BASE_URL}/uploads/{audio_name}"
    }

    tracks = read_tracks()
    tracks.append(track)
    save_tracks(tracks)

    return {"ok": True, "track": track}
