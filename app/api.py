import json
import asyncio
import time
import shutil
import urllib.parse
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException, Request, Body
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- FIXED IMPORTS (Relative for 'app' folder) ---
from . import database
from .school_id_processor import SchoolIDProcessor, CONFIG

# ==================== WEBSOCKET MANAGER ====================
class ConnectionManager:
    def __init__(self): self.active_connections: list[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections: self.active_connections.remove(websocket)
    async def broadcast(self, message: dict):
        for connection in self.active_connections[:]:
            try: await connection.send_json(message)
            except: self.disconnect(connection)

manager = ConnectionManager()

# ==================== WATCHDOG ====================
class IDGenerationHandler(FileSystemEventHandler):
    def __init__(self, processor, loop):
        self.processor = processor
        self.loop = loop
        self.processing = set()

    def on_created(self, event):
        if event.is_directory: return
        filepath = event.src_path
        if not filepath.lower().endswith(('.jpg', '.jpeg', '.png')): return
        if filepath in self.processing: return
        self.processing.add(filepath)

        print(f"\nNew photo detected: {Path(filepath).name}")
        time.sleep(0.5) 
        
        try:
            success = self.processor.process_photo(filepath)
            if success:
                student_id = Path(filepath).stem
                front_file = f"{student_id}_FRONT.png"
                back_file = f"{student_id}_BACK.png"
                
                msg = {
                    "type": "new_id",
                    "student_id": student_id,
                    "front_url": f"/output/{urllib.parse.quote(front_file)}",
                    "back_url": f"/output/{urllib.parse.quote(back_file)}"
                }
                if self.loop and self.loop.is_running():
                    asyncio.run_coroutine_threadsafe(manager.broadcast(msg), self.loop)

        except Exception as e: print(f"CRITICAL ERROR: {e}")
        finally: self.processing.remove(filepath)

# ==================== APP LIFECYCLE ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure folders exist
    Path(CONFIG['OUTPUT_FOLDER']).mkdir(parents=True, exist_ok=True)
    Path(CONFIG['INPUT_FOLDER']).mkdir(parents=True, exist_ok=True)
    Path(CONFIG['TEMPLATE_FOLDER']).mkdir(parents=True, exist_ok=True)
    database.init_db()
    
    main_loop = asyncio.get_running_loop()
    processor = SchoolIDProcessor(CONFIG)
    event_handler = IDGenerationHandler(processor, main_loop)
    observer = Observer()
    observer.schedule(event_handler, CONFIG['INPUT_FOLDER'], recursive=False)
    observer.start()
    
    app.state.processor = processor
    app.state.observer = observer
    print(f"System Online: Watching {CONFIG['INPUT_FOLDER']}")
    yield
    app.state.observer.stop()
    app.state.observer.join()

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ==================== ROUTES ====================

@app.get("/")
async def read_index(): return FileResponse('web/index.html')

@app.get("/index.html")
async def read_index_explicit(): return FileResponse('web/index.html')

@app.get("/dashboard")
async def read_dashboard(): return FileResponse('web/dashboard.html')

@app.get("/editor")
async def read_editor(): return FileResponse('web/editor.html')

@app.get("/layout")
def get_layout():
    try:
        path = CONFIG.get('LAYOUT_FILE', 'data/layout.json')
        with open(path, 'r') as f: return json.load(f)
    except: return {}

@app.post("/layout")
async def save_layout(request: Request):
    data = await request.json()
    path = CONFIG.get('LAYOUT_FILE', 'data/layout.json')
    with open(path, 'w') as f: json.dump(data, f, indent=4)
    return {"status": "saved"}

@app.get("/settings")
def get_settings():
    try:
        with open('data/settings.json', 'r') as f: return json.load(f)
    except: return {}

@app.post("/settings")
async def save_settings(request: Request):
    data = await request.json()
    with open('data/settings.json', 'w') as f: json.dump(data, f, indent=4)
    app.state.processor.reload_config() 
    return {"status": "saved"}

@app.get("/templates/list")
def list_templates():
    files = [f.name for f in Path(CONFIG['TEMPLATE_FOLDER']).glob("*.png")]
    return files

@app.post("/templates/upload")
async def upload_template(file: UploadFile = File(...)):
    save_path = Path(CONFIG['TEMPLATE_FOLDER']) / file.filename
    with open(save_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    return {"status": "uploaded", "filename": file.filename}

@app.get("/students")
def get_students(): return database.get_all_students()

@app.post("/students/update")
async def update_student(data: dict = Body(...)):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    sql = """
        UPDATE students 
        SET full_name=%s, lrn=%s, grade_level=%s, section=%s, 
            guardian_name=%s, address=%s, guardian_contact=%s 
        WHERE id_number=%s
    """
    val = (
        data['name'], data['lrn'], data['grade_level'], data['section'], 
        data['guardian_name'], data['address'], data['guardian_contact'], 
        data['id']
    )
    cursor.execute(sql, val)
    conn.commit()
    conn.close()
    return {"status": "updated"}

@app.post("/regenerate/{student_id}")
async def regenerate_id(student_id: str):
    raw_path = Path(CONFIG['INPUT_FOLDER']) / f"{student_id}.jpg"
    if not raw_path.exists(): raw_path = Path(CONFIG['INPUT_FOLDER']) / f"{student_id}.png"
    
    if raw_path.exists():
        success = app.state.processor.process_photo(str(raw_path))
        return {"status": "regenerated" if success else "failed"}
    else:
        raise HTTPException(status_code=404, detail="Original photo not found")

@app.get("/history")
def get_history(): 
    history = database.get_recent_history(limit=50)
    enhanced_history = []
    for h in history:
        sid = h['student_id']
        enhanced_history.append({
            **h,
            "front_url": f"/output/{sid}_FRONT.png",
            "back_url": f"/output/{sid}_BACK.png"
        })
    return enhanced_history

# --- UPDATED CAPTURE ENDPOINT ---
@app.post("/capture")
async def upload_capture(
    file: UploadFile = File(...), 
    student_id: str = Form(...),
    # Manual Fields
    manual_name: str = Form(None),
    manual_grade: str = Form(None),
    manual_section: str = Form(None),
    manual_guardian: str = Form(None), # NEW
    manual_address: str = Form(None),  # NEW
    manual_contact: str = Form(None)   # NEW
):
    try:
        # 1. If manual data exists, save it to a JSON sidecar file
        if manual_name:
            json_path = Path(CONFIG['INPUT_FOLDER']) / f"{student_id}.json"
            manual_data = {
                "id_number": student_id,
                "full_name": manual_name,
                "grade_level": manual_grade or "",
                "section": manual_section or "",
                # Capture the new Back of ID fields
                "guardian_name": manual_guardian or "", 
                "address": manual_address or "", 
                "guardian_contact": manual_contact or "",
                "lrn": "" # Default empty
            }
            with open(json_path, 'w') as f:
                json.dump(manual_data, f)
            print(f"Manual data saved for {student_id}")

        # 2. Save the image (Triggers Watchdog)
        filename = f"{student_id}.jpg"
        save_path = Path(CONFIG['INPUT_FOLDER']) / filename
        with open(save_path, "wb") as buffer: 
            shutil.copyfileobj(file.file, buffer)
            
        return {"status": "saved", "path": str(save_path)}
    except Exception as e: 
        print(f"Capture Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True: await websocket.receive_text()
    except WebSocketDisconnect: manager.disconnect(websocket)

app.mount("/output", StaticFiles(directory=CONFIG['OUTPUT_FOLDER']), name="output")
app.mount("/templates", StaticFiles(directory=CONFIG['TEMPLATE_FOLDER']), name="templates")