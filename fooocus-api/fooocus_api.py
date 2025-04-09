from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pathlib import Path
import base64
import os

app = FastAPI()

@app.post("/get-latest-fooocus-image")
def get_latest_image():
    outputs_dir = Path("/home/seventy7llm/Fooocus/outputs")
    image_files = sorted(outputs_dir.rglob("*.png"), key=os.path.getmtime, reverse=True)

    if not image_files:
        return JSONResponse({"response": "No images found."})

    latest = image_files[0]

    try:
        with open(latest, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return JSONResponse({
            "response": f"![Latest Fooocus Image](data:image/png;base64,{encoded})"
        })
    except Exception as e:
        return JSONResponse({"response": f"Error: {str(e)}"})
