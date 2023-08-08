from fastapi import Form, File, UploadFile, Request, FastAPI
from typing import List
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.post("/submit")
def submit(
    # name: str = Form(...),
    # point: float = Form(...),
    # is_accepted: bool = Form(...),
    files: List[UploadFile] = File(...),
):
    return {
        # "JSON Payload ": {"name": name, "point": point, "is_accepted": is_accepted},
        "Filenames": [file.filename for file in files],
    }


# @app.get("/", response_class=HTMLResponse)
# def main(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})