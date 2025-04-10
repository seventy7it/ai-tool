import os
import base64
from pathlib import Path
from fastapi import FastAPI

app = FastAPI()  # <- THIS is required by uvicorn

@app.post("/get-latest-fooocus-image")
def get_latest_image():
    base_path = "/home/seventy7llm/Fooocus/outputs"

    def get_latest_image_path(folder: str) -> Path | None:
        pngs = sorted(Path(folder).rglob("*.png"), key=os.path.getmtime, reverse=True)
        return pngs[0] if pngs else None

    try:
        folders = sorted(Path(base_path).glob("*"), key=os.path.getmtime, reverse=True)
        if not folders:
            return {"type": "text", "content": "No folders found."}

        latest_folder = folders[0]
        image_path = get_latest_image_path(str(latest_folder))
        if not image_path:
            return {"type": "text", "content": "No PNGs found."}

        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return {
            "type": "image",
            "content": f"data:image/png;base64,{encoded}"
        }

    except Exception as e:
        return {"type": "text", "content": f"Error: {str(e)}"}
