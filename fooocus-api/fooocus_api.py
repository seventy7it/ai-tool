import os
import shutil
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()
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
        folders = sorted(Path(base_path).glob("*"), key=os.path.getmtime, reverse=True)
        if not folders:
            return {"response": "❌ No subfolders found in Fooocus output."}

        latest_folder = folders[0]
        image_path = get_latest_focus_image(str(latest_folder))
        if not image_path:
            return {"response": "❌ No PNG images found in latest folder."}

        static_img_path = Path(STATIC_DIR) / "latest.png"
        shutil.copyfile(image_path, static_img_path)

        return {
            "type": "image_url",
            "content": "http://10.55.2.11:8001/static/latest.png"
        }
    except Exception as e:
        return {"response": f"🔥 Error: {str(e)}"}
