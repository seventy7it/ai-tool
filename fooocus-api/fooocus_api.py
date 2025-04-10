# fooocus_api.py
import os
import base64
from fastapi import FastAPI
from pathlib import Path

app = FastAPI()

def get_latest_focus_image(image_folder: str) -> Path | None:
    print(f"🔍 Searching for .png files in: {image_folder}")
    pngs = sorted(Path(image_folder).rglob("*.png"), key=os.path.getmtime, reverse=True)
    print(f"📸 Found {len(pngs)} image(s)")
    return pngs[0] if pngs else None

@app.post("/get-latest-fooocus-image")
def get_latest_image():
    base_path = "/home/seventy7llm/Fooocus/outputs"
    try:
        print(f"📁 Scanning base output path: {base_path}")
        folders = sorted(Path(base_path).glob("*"), key=os.path.getmtime, reverse=True)
        print(f"📂 Found folders: {[f.name for f in folders]}")

        if not folders:
            return {"type": "text", "content": "❌ No subfolders found in Fooocus output."}

        latest_folder = folders[0]
        print(f"🆕 Latest folder: {latest_folder}")

        image_path = get_latest_focus_image(str(latest_folder))
        print(f"🖼️ Latest image path: {image_path}")

        if not image_path:
            return {"type": "text", "content": "❌ No PNG images found in the latest folder."}

        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")

        return {
            "type": "image",
            "content": f"data:image/png;base64,{encoded}"
        }

    except Exception as e:
        print(f"🔥 Error: {e}")
        return {"type": "text", "content": f"🔥 Error: {str(e)}"}
