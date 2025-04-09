# fooocus_api.py
import os
import base64
from datetime import datetime
from fastapi import FastAPI
from pathlib import Path

app = FastAPI()

def get_latest_focus_image(image_folder: str) -> Path | None:
    # Recursively search for .png files in all subfolders
    pngs = sorted(Path(image_folder).rglob("*.png"), key=os.path.getmtime, reverse=True)
    return pngs[0] if pngs else None

@app.post("/get-latest-fooocus-image")
def get_latest_image():
    base_path = "/home/seventy7llm/Fooocus/outputs"
    try:
        # Find latest subfolder
        folders = sorted(Path(base_path).glob("*"), key=os.path.getmtime, reverse=True)
        if not folders:
            return {"response": "No folders found."}

        latest_folder = folders[0]
        image_path = get_latest_focus_image(str(latest_folder))
        if not image_path:
            return {"response": "No PNGs found."}

        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")
        return {"response": f"data:image/png;base64,{encoded}"}

    except Exception as e:
        return {"response": f"Error: {str(e)}"}
