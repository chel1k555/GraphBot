from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
import uuid
import lib.LLMRequests as LLM
import lib.data as dataConventer
import lib.prompt as promptGenerator
import lib.graphs as graphs
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# В памяти храним:
# session_id -> {
#     file_path: "...",
#     lst: [...]
# }
SESSIONS = {}

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()
    

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    session_id = str(uuid.uuid4())
    file_path = f"{UPLOAD_FOLDER}/{session_id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    df = pd.read_excel(file_path)
    profile = dataConventer.profileDataframe(df)
    sample_rows = df.head(6)

    userPrompt = promptGenerator.userPrompt(profile, sample_rows)
    systemPrompt = promptGenerator.systemPrompt()
    
    # Получаем рекомендации от LLM (с повтором при ошибке парсинга)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = LLM.GetLLMResponse(userPrompt, systemPrompt, debugMessages=True)
            break
        except ValueError as e:
            if attempt < max_retries - 1:
                print(f"LLM attempt {attempt + 1} failed: {e}. Retrying...")
            else:
                raise

    # Фильтруем рекомендации, которые невозможно построить
    valid = [r for r in result if graphs.validate_chart_config(file_path, r)]

    # Фильтруем рекомендации, которые невозможно построить
    valid = [r for r in result if graphs.validate_chart_config(file_path, r)]

    SESSIONS[session_id] = {
        "file_path": file_path,
        "lst": valid
    }

    return {
        "session_id": session_id,
        "recommendations": valid
    }

@app.post("/build_chart")
async def build_chart(data: dict):

    session_id = data["session_id"]
    chart_index = data["chart_index"]
    colors = data.get("colors")

    session = SESSIONS.get(session_id)
    if not session:
        return {"error": "Session not found"}

    file_path = session["file_path"]
    chart_config = session["lst"][chart_index]

    try:
        image_path = graphs.generate_chart(
            file_path,
            chart_config,
            colors=colors
        )
    except (ValueError, KeyError, IndexError) as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    return FileResponse(image_path, media_type="image/png")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/", StaticFiles(directory="templates"), name="templates")

