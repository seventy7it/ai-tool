# fooocus_api.py
import os
import base64
from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil

app = FastAPI()

# Serve static files (optional, for URL mode)
STATIC_DIR = "/home/seventy7llm/my-docs/fooocus-api/static"
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def get_latest_focus_image(image_folder: str) -> Path | None:
    pngs = sorted(Path(image_folder).rglob("*.png"), key=os.path.getmtime, reverse=True)
    return pngs[0] if pngs else None

@app.post("/get-latest-fooocus-image")
def get_latest_image():
    base_path = "/home/seventy7llm/Fooocus/outputs"
    try:
        # Find most recent dated folder
        folders = sorted(Path(base_path).glob("*"), key=os.path.getmtime, reverse=True)
        if not folders:
            return {"type": "text", "content": "❌ No subfolders found in Fooocus output."}

        latest_folder = folders[0]
        image_path = get_latest_focus_image(str(latest_folder))
        if not image_path:
            return {"type": "text", "content": "❌ No PNG images found in latest folder."}

        # Optionally also copy image to static/latest.png (not used in this return method)
        static_img_path = Path(STATIC_DIR) / "latest.png"
        shutil.copyfile(image_path, static_img_path)

        # ✅ Encode as base64 and return inline image
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")

        return {
            "type": "image",
            "content": f"data:image/png;base64,{encoded}"
        }

    except Exception as e:
        return {"type": "text", "content": f"🔥 Error: {str(e)}"}
