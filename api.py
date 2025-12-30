import asyncio
import time
import shutil
import urllib.parse
import database
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse 
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from school_id_processor import SchoolIDProcessor, CONFIG

# ==================== WEBSOCKET ====================
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections[:]:
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

# ==================== WATCHDOG ====================
class IDGenerationHandler(FileSystemEventHandler):
    def __init__(self, processor):
        self.processor = processor
        self.processing = set()

    def on_created(self, event):
        if event.is_directory: return
        filepath = event.src_path
        if not filepath.lower().endswith(('.jpg', '.jpeg', '.png')): return
        
        if filepath in self.processing: return
        self.processing.add(filepath)

        print(f"\n📸 New photo detected: {Path(filepath).name}")
        time.sleep(0.5) 
        
        try:
            success = self.processor.process_photo(filepath)
            
            if success:
                student_id = Path(filepath).stem
                output_filename = f"{student_id}_FINAL.png"
                output_path = Path(CONFIG['OUTPUT_FOLDER']) / output_filename
                
                # SAFETY CHECK: Wait for file to be fully written
                attempts = 0
                while attempts < 20:
                    if output_path.exists() and output_path.stat().st_size > 0:
                        break
                    time.sleep(0.2)
                    attempts += 1
                
                if output_path.exists() and output_path.stat().st_size > 0:
                    print(f"📡 Broadcasting to Frontend: {output_filename}")
                    safe_filename = urllib.parse.quote(output_filename)
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(manager.broadcast({
                        "type": "new_id",
                        "student_id": student_id,
                        "image_url": f"/output/{safe_filename}" # Relative path
                    }))
                    loop.close()
                else:
                    print(f"❌ Error: File {output_filename} missing or empty.")

        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
        finally:
            self.processing.remove(filepath)

# ==================== APP LIFECYCLE ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(CONFIG['OUTPUT_FOLDER']).mkdir(parents=True, exist_ok=True)
    Path(CONFIG['INPUT_FOLDER']).mkdir(parents=True, exist_ok=True)
    
    database.init_db()
    
    processor = SchoolIDProcessor(CONFIG)
    event_handler = IDGenerationHandler(processor)
    observer = Observer()
    observer.schedule(event_handler, CONFIG['INPUT_FOLDER'], recursive=False)
    observer.start()
    app.state.observer = observer
    
    print(f"👀 System Online: Watching {CONFIG['INPUT_FOLDER']}")
    yield
    app.state.observer.stop()
    app.state.observer.join()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/output", StaticFiles(directory=CONFIG['OUTPUT_FOLDER']), name="output")

# ==================== ENDPOINTS ====================

# NEW: Serve the Interface directly from Python!
@app.get("/")
async def read_index():
    return FileResponse('index.html')

@app.get("/students")
def get_students():
    return database.get_all_students()

@app.get("/history")
def get_history():
    return database.get_recent_history()

@app.post("/capture")
async def upload_capture(file: UploadFile = File(...), student_id: str = Form(...)):
    try:
        filename = f"{student_id}.jpg"
        save_path = Path(CONFIG['INPUT_FOLDER']) / filename
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"status": "saved", "path": str(save_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    # IMPORTANT: We listen on all interfaces
    print("\n" * 2)
    print("="*60)
    print("   RIMBERIO ID SYSTEM ONLINE")
    print("   👉 OPEN THIS LINK: http://localhost:8000")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8000)