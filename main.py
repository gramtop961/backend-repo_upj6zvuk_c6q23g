import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal, Dict, Any, Optional

from database import create_document, get_documents, db
from schemas import VideoJob

app = FastAPI(title="Auto YouTube Video Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Auto YouTube Video Generator Backend Running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# --------- Action payload models (mirror the agent action schemas) ---------

class GenerateVoicePayload(BaseModel):
    script: str
    voice: str

class GenerateBrollPayload(BaseModel):
    scene_prompts: List[str]

class AutoEditPayload(BaseModel):
    voiceover_url: str
    broll_urls: List[str]
    style: str
    format: str

# --------- Job endpoints to orchestrate the pipeline ---------

@app.post("/api/jobs", response_model=Dict[str, Any])
def create_job(job: VideoJob):
    try:
        job_id = create_document("videojob", job)
        return {"id": job_id, "status": job.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs", response_model=List[Dict[str, Any]])
def list_jobs(limit: int = 20):
    try:
        docs = get_documents("videojob", limit=limit)
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Stubs to simulate Flames.Blue agent action integrations.
# In your environment, your master agent should call these or be called by these.

@app.post("/api/actions/generate_voice")
def action_generate_voice(payload: GenerateVoicePayload):
    return {"voiceover_url": "https://example.com/voiceover.mp3"}

@app.post("/api/actions/generate_broll")
def action_generate_broll(payload: GenerateBrollPayload):
    urls = [f"https://example.com/broll_{i}.mp4" for i, _ in enumerate(payload.scene_prompts, start=1)]
    return {"broll_urls": urls}

@app.post("/api/actions/auto_edit_video")
def action_auto_edit(payload: AutoEditPayload):
    return {"final_url": "https://example.com/final_video.mp4"}

# --------- Full pipeline runner ---------

class RunRequest(BaseModel):
    trigger_phrase: str = "Create a full video automatically."
    topic: Optional[str] = None
    voice: str = "male_tech_voice"
    style: str = "tech_fastpaced"
    format: str = "1080p"

@app.post("/api/run")
def run_pipeline(req: RunRequest):
    if req.trigger_phrase.strip() != "Create a full video automatically.":
        raise HTTPException(status_code=400, detail="Invalid trigger phrase")

    # 1) Trend detection (mock)
    topic = req.topic or "Why AI copilots are changing software in 2025"
    trend = {
        "topic": topic,
        "why": "Mass adoption in IDEs and office suites",
        "viral_score": 87,
        "angle": "Pros & cons with real examples"
    }

    # 2) Script generation (mock)
    script = (
        f"Title: {topic}\n\n" 
        "Intro: In this video, we explore how AI copilots...\n" 
        "...\nConclusion: Subscribe for more!"
    )
    scenes = [
        "Developer coding with AI suggestions on screen",
        "Graph showing productivity improvements",
        "Security team reviewing AI-generated code",
    ]

    # 3) Voiceover
    voice_res = action_generate_voice(GenerateVoicePayload(script=script, voice=req.voice))

    # 4) B-roll
    broll_res = action_generate_broll(GenerateBrollPayload(scene_prompts=scenes))

    # 5) Auto edit
    edit_res = action_auto_edit(
        AutoEditPayload(
            voiceover_url=voice_res["voiceover_url"],
            broll_urls=broll_res["broll_urls"],
            style=req.style,
            format=req.format,
        )
    )

    # 6) Final output and persist job
    job = VideoJob(
        topic=topic,
        voice=req.voice,
        style=req.style,
        format=req.format,
        status="completed",
        step="Final MP4 Output",
        progress=100,
        script=script,
        voiceover_url=voice_res["voiceover_url"],
        broll_urls=broll_res["broll_urls"],
        final_url=edit_res["final_url"],
        logs=["Pipeline executed (mock)"]
    )
    try:
        job_id = create_document("videojob", job)
    except Exception:
        job_id = None

    return {
        "job_id": job_id,
        "trend": trend,
        "script": script,
        "voiceover_url": voice_res["voiceover_url"],
        "broll_urls": broll_res["broll_urls"],
        "final_url": edit_res["final_url"],
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
