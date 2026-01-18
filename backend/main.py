import sys
import os
import shutil
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import logging

# Ensure services are importable
sys.path.append(os.path.join(os.path.dirname(__file__), "services"))

from services.stt_service import stt_service
from services.nlu_service import nlu_service
from services.tts_service import tts_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_avatar_backend")

app = FastAPI(title="AI Avatar LMS Backend")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.websocket("/ws/avatar")
async def avatar_stream(websocket: WebSocket):
    await websocket.accept()
    logger.info("Client connected to WebSocket")
    
    try:
        while True:
            # Protocol: Client sends either JSON command or Binary Audio
            # For MVP simplicity: Client sends text message "start_audio" -> sends binary audio -> sends text "end_audio"?
            # Or simpler: Client sends binary blob of the whole recording.
            
            message = await websocket.receive()
            
            if "bytes" in message:
                # Received audio data
                audio_data = message["bytes"]
                file_id = str(uuid.uuid4())
                # Browsers usually send WebM/Ogg
                input_file = os.path.join(TEMP_DIR, f"{file_id}.webm")
                
                with open(input_file, "wb") as f:
                    f.write(audio_data)
                
                logger.info(f"Received audio ({len(audio_data)} bytes), saved to {input_file}")
                
                # 1. STT
                transcript = stt_service.transcribe(input_file)
                logger.info(f"Transcript: {transcript}")
                
                # Verify transcript is not empty
                if not transcript:
                    transcript = "I didn't catch that."
                
                # Send transcript back to UI
                await websocket.send_json({"type": "transcript", "text": transcript})
                
                # 2. NLU / Intent
                nlu_response = nlu_service.process_text(transcript)
                response_text = nlu_response["text"]
                action = nlu_response.get("action")
                data = nlu_response.get("data")
                
                # 3. TTS
                audio_url = tts_service.generate_audio(response_text)
                
                logger.info(f"AI Response: {response_text}, Audio: {audio_url}")
                await websocket.send_json({
                    "type": "response_text", 
                    "text": response_text,
                    "audio_url": audio_url,
                    "action": action,
                    "data": data
                })
                
                # Cleanup
                if os.path.exists(input_file):
                    os.remove(input_file)
                    
            elif "text" in message:
                # Handle control messages if any
                text = message["text"]
                logger.info(f"Received text: {text}")
                if text == "ping":
                    await websocket.send_text("pong")

    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
