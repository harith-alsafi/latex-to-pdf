from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import subprocess
import uuid
import base64
import shutil

def is_pdflatex_available() -> bool:
    return shutil.which("pdflatex") is not None

app = FastAPI()

BASE_DIR = "latex_workspace"

class FileItem(BaseModel):
    name: Optional[str] = None
    main: Optional[bool] = False
    content: str

class CompileRequest(BaseModel):
    userId: str
    templateId: str
    compileCommand: Optional[str] = None
    files: List[FileItem]

@app.post("/compile")
async def compile_latex(req: CompileRequest):
    if not is_pdflatex_available():
        return JSONResponse(
            status_code=500,
            content={"error": "pdflatex is not installed or not in PATH."}
        )

    # Create user and template folders
    user_path = os.path.join(BASE_DIR, req.userId)
    template_path = os.path.join(user_path, req.templateId)
    os.makedirs(template_path, exist_ok=True)

    main_tex_file = None

    # Save each file
    for f in req.files:
        filename = f.name
        if not filename:
            if f.main:
                filename = "main.tex"
            else:
                return HTTPException(status_code=400, detail="Non-main files must have a name")

        file_path = os.path.join(template_path, filename)
        
        # Decode base64 images if necessary
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            with open(file_path, 'wb') as img_file:
                img_file.write(base64.b64decode(f.content))
        else:
            with open(file_path, 'w', encoding='utf-8') as text_file:
                text_file.write(f.content)

        if f.main:
            main_tex_file = filename

    if not main_tex_file:
        return JSONResponse(status_code=400, content={"error": "No main LaTeX file specified."})

    # Compilation
    output_pdf = os.path.join(template_path, "output.pdf")

    try:
        if req.compileCommand:
            command = req.compileCommand
        else:
            command = f"pdflatex -interaction=nonstopmode -output-directory={template_path} {os.path.join(template_path, main_tex_file)}"

        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            timeout=30
        )

        if proc.returncode != 0 or not os.path.exists(output_pdf):
            return JSONResponse(
                status_code=400,
                content={"error": "Compilation failed", "log": proc.stdout.decode() + proc.stderr.decode()}
            )

        return FileResponse(output_pdf, media_type="application/pdf", filename="output.pdf")

    except subprocess.TimeoutExpired:
        return JSONResponse(status_code=500, content={"error": "Compilation timeout."})
