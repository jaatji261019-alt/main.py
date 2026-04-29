from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import edge_tts

app = FastAPI(title="Voxify TTS API 🚀")

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # production me specific domain use karna
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= ROOT =================
@app.get("/")
def home():
    return {"status": "API is running 🚀"}

# ================= HEALTH =================
@app.get("/health")
def health():
    return {"status": "ok"}

# ================= MODEL =================
class TTSRequest(BaseModel):
    text: str
    voice: str = "en-US-AriaNeural"

# ================= VOICES API =================
@app.get("/voices")
async def get_voices():
    try:
        voices = await edge_tts.list_voices()

        return [
            {
                "name": v["ShortName"],
                "gender": v["Gender"],
                "lang": v["Locale"],
                "friendly": v["FriendlyName"]
            }
            for v in voices
        ]

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ================= TTS =================
@app.post("/tts")
async def tts(req: TTSRequest):

    # basic validation
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    try:
        async def audio_stream():
            communicate = edge_tts.Communicate(
                text=req.text,
                voice=req.voice
            )

            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    yield chunk["data"]

        return StreamingResponse(audio_stream(), media_type="audio/mpeg")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
