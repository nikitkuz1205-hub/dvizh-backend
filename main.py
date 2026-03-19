import json
import os
import shutil
from uuid import uuid4

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
TRACKS_FILE = os.path.join(BASE_DIR, "tracks.json")

os.makedirs(UPLOADS_DIR, exist_ok=True)

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


def read_tracks():
    with open(TRACKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tracks(tracks):
    with open(TRACKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tracks, f, ensure_ascii=False, indent=2)


@app.get("/tracks")
def get_tracks():
    return read_tracks()


@app.post("/upload")
async def upload_track(
    title: str = Form(...),
    artist: str = Form(...),
    audio: UploadFile = File(...),
):
    ext = os.path.splitext(audio.filename)[1].lower()
    if ext not in [".mp3", ".wav", ".m4a"]:
        return {"error": "Поддерживаются только .mp3, .wav, .m4a"}

    unique_name = f"{uuid4().hex}{ext}"
    file_path = os.path.join(UPLOADS_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    track = {
        "title": title,
        "artist": artist,
        "cover": "https://placehold.co/500x500/171717/FFFFFF?text=%D0%94%D0%B2%D0%B8%D0%B6",
        "src": f"http://127.0.0.1:8000/uploads/{unique_name}"
    }

    tracks = read_tracks()
    tracks.append(track)
    save_tracks(tracks)

    return {"ok": True, "track": track}