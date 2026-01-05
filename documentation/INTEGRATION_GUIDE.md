# Backend-Frontend Integration Guide
## School ID Automation System - React UI Migration

**Generated:** January 5, 2026  
**Frontend:** React 18.3.1 + Vite 6.0.1 + Tailwind CSS 3.4.15  
**Backend:** Python FastAPI (Port 8000)

---

## 📋 Overview of Recent Changes

### What Was Changed
The entire UI has been **completely rebuilt** from vanilla HTML/JavaScript to a modern React-based Single Page Application (SPA):

**Old UI (Removed):**
- `web/index.html` - Static capture station page
- `web/dashboard.html` - Static dashboard page  
- `web/editor.html` - Static layout editor page
- Direct JavaScript manipulation of DOM
- No component reusability
- Manual state management

**New UI (Created):**
- Modern React SPA in `UI/` directory
- 50+ modular components with TypeScript-style JSDoc
- Tailwind CSS design system with custom navy color palette
- React Router for client-side navigation
- Context API for global state management
- Custom hooks for API interactions
- Real-time WebSocket integration
- Hot Module Replacement (HMR) for development

---

## 🔌 Current Connection Status

### ✅ Configured (Ready for Connection)
The frontend is **properly configured** to connect to the backend but requires the backend server to be running:

**Frontend Configuration:**
- **Dev Server:** http://localhost:5173 (Vite)
- **API Proxy:** `/api/*` → `http://localhost:8000/api/*`
- **WebSocket Proxy:** `/ws` → `ws://localhost:8000/ws`

**Backend Configuration:**
- **Server:** http://localhost:8000 (FastAPI)
- **CORS:** Enabled for all origins
- **Static Files:** Serving `/output` and `/templates` directories

### ⚠️ Not Yet Connected
The frontend is running but showing connection errors because:
1. The Python backend server is not currently running
2. The backend still references old HTML files in routes
3. The backend needs to serve the new React build in production

---

## 🔧 Backend API Endpoint Mapping

### Current Backend Routes vs Frontend Expectations

| Frontend Hook | Expected Endpoint | Backend Route | Status |
|--------------|-------------------|---------------|---------|
| WebSocketContext | `/ws` | `@app.websocket("/ws")` | ✅ Exists |
| SettingsContext | `GET/POST /api/settings` | `GET/POST /settings` | ⚠️ Missing `/api` prefix |
| useStudents | `GET /api/students` | `GET /students` | ⚠️ Missing `/api` prefix |
| useStudents | `POST /api/students/update` | `POST /students/update` | ⚠️ Missing `/api` prefix |
| useHistory | `GET /api/history` | `GET /history` | ⚠️ Missing `/api` prefix |
| useTemplates | `GET /api/templates/list` | `GET /templates/list` | ⚠️ Missing `/api` prefix |
| useTemplates | `POST /api/templates/upload` | `POST /templates/upload` | ⚠️ Missing `/api` prefix |
| useTemplates | `DELETE /api/templates/{name}` | ❌ Not implemented | ❌ Missing |
| Capture | `POST /api/capture` | `POST /capture` | ⚠️ Missing `/api` prefix |
| Dashboard | `POST /api/regenerate/{id}` | `POST /regenerate/{id}` | ⚠️ Missing `/api` prefix |
| Editor | `GET/POST /api/layout` | `GET/POST /layout` | ⚠️ Missing `/api` prefix |

---

## 🚀 Step-by-Step Integration Instructions

### Phase 1: Update Backend API Routes (Required)

The backend needs to add `/api` prefix to all routes to match frontend expectations:

**File:** `app/api.py`

```python
# BEFORE (Current):
@app.get("/settings")
def get_settings():
    # ...

# AFTER (Required):
@app.get("/api/settings")
def get_settings():
    # ...
```

**Complete List of Routes to Update:**

```python
# Settings
@app.get("/api/settings")
@app.post("/api/settings")

# Layout
@app.get("/api/layout")
@app.post("/api/layout")

# Templates
@app.get("/api/templates/list")
@app.post("/api/templates/upload")
@app.delete("/api/templates/{filename}")  # NEW - needs implementation

# Students
@app.get("/api/students")
@app.post("/api/students/update")

# History
@app.get("/api/history")

# Capture
@app.post("/api/capture")

# Regenerate
@app.post("/api/regenerate/{student_id}")

# WebSocket (already correct)
@app.websocket("/ws")  # No change needed
```

**New Route to Add (Template Deletion):**

```python
from fastapi import HTTPException

@app.delete("/api/templates/{filename}")
async def delete_template(filename: str):
    """Delete a template file"""
    template_path = Path(CONFIG['TEMPLATE_FOLDER']) / filename
    
    if not template_path.exists():
        raise HTTPException(status_code=404, detail="Template not found")
    
    try:
        template_path.unlink()
        return {"status": "deleted", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Phase 2: Update Backend to Serve React App

**Option A: Development Mode (Recommended for Testing)**

Keep both servers running separately:
```powershell
# Terminal 1: Backend (Python)
cd c:\School_IDs
.\venv\Scripts\activate
uvicorn app.api:app --reload --port 8000

# Terminal 2: Frontend (React)
cd c:\School_IDs\UI
npm run dev
```

Access the app at: **http://localhost:5173**

**Option B: Production Mode (Build and Serve)**

Build the React app and serve it from FastAPI:

```powershell
# Build the React app
cd c:\School_IDs\UI
npm run build  # Creates UI/dist folder
```

Update `app/api.py`:

```python
# Remove old HTML routes
# DELETE these lines:
@app.get("/")
async def read_index(): return FileResponse('web/index.html')

@app.get("/index.html")
async def read_index_explicit(): return FileResponse('web/index.html')

@app.get("/dashboard")
async def read_dashboard(): return FileResponse('web/dashboard.html')

@app.get("/editor")
async def read_editor(): return FileResponse('web/editor.html')

# ADD this at the end of app/api.py (before app.mount for output/templates):
from fastapi.responses import HTMLResponse

# Serve React app
app.mount("/assets", StaticFiles(directory="UI/dist/assets"), name="assets")

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_react_app(full_path: str):
    """Serve React SPA for all non-API routes"""
    # Serve index.html for all routes (React Router handles client-side routing)
    return FileResponse('UI/dist/index.html')
```

Start the backend:
```powershell
cd c:\School_IDs
.\venv\Scripts\activate
uvicorn app.api:app --reload --port 8000
```

Access the app at: **http://localhost:8000**

### Phase 3: Remove Old UI Files

Once the new React UI is working, remove the old HTML files:

```powershell
# Remove old UI directory
cd c:\School_IDs
Remove-Item -Recurse -Force web
```

Or manually delete:
- `web/index.html`
- `web/dashboard.html`
- `web/editor.html`

### Phase 4: Test the Integration

**Start Backend:**
```powershell
cd c:\School_IDs
.\venv\Scripts\activate
uvicorn app.api:app --reload --port 8000
```

**Start Frontend (Dev Mode):**
```powershell
cd c:\School_IDs\UI
npm run dev
```

**Verification Checklist:**

1. **WebSocket Connection:**
   - Open http://localhost:5173
   - Check browser console (F12)
   - Should see: "WebSocket connected" (not "WebSocket connection error")

2. **Settings Page:**
   - Navigate to Settings (gear icon)
   - Change enhancement strength slider
   - Click "Save Changes"
   - Verify settings persist on page reload

3. **Dashboard:**
   - Navigate to Dashboard
   - Student table should load with data
   - Try editing a student record

4. **Capture Station:**
   - Navigate to Capture (camera icon)
   - Select camera from dropdown
   - Video feed should appear
   - Test capture functionality

5. **Layout Editor:**
   - Navigate to Editor
   - Templates should load in dropdown
   - Layout elements should be draggable

---

## 📁 Project Structure After Migration

```
School_IDs/
├── app/                          # Backend (Python)
│   ├── __init__.py
│   ├── api.py                    # FastAPI server (NEEDS UPDATES)
│   ├── database.py
│   ├── school_id_processor.py
│   └── ...
├── UI/                           # Frontend (React) - NEW
│   ├── src/
│   │   ├── components/
│   │   │   ├── capture/         # Capture Station page
│   │   │   ├── dashboard/       # Dashboard page
│   │   │   ├── editor/          # Layout Editor page
│   │   │   ├── layout/          # Navigation components
│   │   │   └── shared/          # Reusable UI components
│   │   ├── contexts/            # Global state management
│   │   ├── hooks/               # Custom API hooks
│   │   ├── utils/               # Helper functions
│   │   ├── App.jsx              # Root component with routing
│   │   ├── main.jsx             # Entry point
│   │   └── index.css            # Tailwind styles
│   ├── package.json
│   ├── vite.config.js           # Dev server + proxy config
│   ├── tailwind.config.js       # Design system tokens
│   └── dist/                    # Production build (after npm run build)
├── web/                          # Old UI - TO BE REMOVED
│   ├── index.html               # ❌ DELETE
│   ├── dashboard.html           # ❌ DELETE
│   └── editor.html              # ❌ DELETE
├── data/                         # JSON configuration files
├── venv/                         # Python virtual environment
└── ...
```

---

## 🎨 Design System Reference

### Color Palette (Custom Navy Theme)
```javascript
navy: {
  950: '#0a0e1f',  // Darkest - Main background
  900: '#0f1729',  // Cards, panels
  800: '#1a2235',  // Elevated elements
  700: '#242d42',  // Borders, dividers
  600: '#2e3a50',  // Hover states
  500: '#3d4a64',  // Active states, text secondary
}
```

### Typography
- **Font Family:** Inter (UI), JetBrains Mono (Code)
- **Font Sizes:** 11px (xs) → 28px (2xl)
- **Line Heights:** 1.2 (tight) → 2 (relaxed)

### Spacing Scale
- Base unit: 4px
- Scale: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80px

### Animation Timings
- Fast: 150ms (hovers, clicks)
- Normal: 200ms (transitions)
- Slow: 300ms (modals, panels)

---

## 🔍 Troubleshooting Common Issues

### Issue 1: "WebSocket connection error"

**Symptoms:**
- Toast notification: "WebSocket connection error"
- Console error: `WebSocket connection to 'ws://localhost:5173/ws' failed`

**Solution:**
- Ensure backend is running: `uvicorn app.api:app --reload --port 8000`
- Check backend logs for WebSocket connection
- Verify CORS is enabled in `app/api.py`

### Issue 2: "Failed to fetch settings"

**Symptoms:**
- Settings page shows loading state indefinitely
- Console error: `GET http://localhost:5173/api/settings net::ERR_FAILED`

**Solution:**
- Update backend routes to include `/api` prefix (see Phase 1)
- Restart backend server after changes

### Issue 3: Template images not loading

**Symptoms:**
- Template thumbnails show broken image icons
- Console error: `GET http://localhost:8000/templates/TEMPLATE_FRONT.png 404`

**Solution:**
- Verify templates exist in `data/Templates/` directory
- Check `CONFIG['TEMPLATE_FOLDER']` in backend configuration
- Ensure `/templates` is mounted in `app/api.py`

### Issue 4: Student photos not displaying

**Symptoms:**
- Generated IDs show broken images
- Console error: `GET http://localhost:8000/output/123456_FRONT.png 404`

**Solution:**
- Verify output images exist in `data/output/` directory
- Check `CONFIG['OUTPUT_FOLDER']` in backend configuration
- Ensure `/output` is mounted in `app/api.py`

### Issue 5: Camera not detected

**Symptoms:**
- Camera dropdown shows "No cameras found"
- Video viewport is blank

**Solution:**
- Allow camera permissions in browser
- Check browser console for permission errors
- Test in Chrome/Edge (better camera support than Firefox)

---

## 📊 API Request/Response Examples

### GET /api/students
**Response:**
```json
[
  {
    "id_number": "123456789",
    "full_name": "Juan Dela Cruz",
    "lrn": "123456789012",
    "grade_level": "Grade 10",
    "section": "Diamond",
    "guardian_name": "Maria Dela Cruz",
    "address": "123 Main St, Manila",
    "guardian_contact": "09171234567"
  }
]
```

### POST /api/capture
**Request (multipart/form-data):**
```
file: [blob] (image file)
student_id: "123456789"
manual_name: "Juan Dela Cruz"
manual_grade: "Grade 10"
manual_section: "Diamond"
manual_guardian: "Maria Dela Cruz"
manual_address: "123 Main St"
manual_contact: "09171234567"
```

**Response:**
```json
{
  "status": "saved",
  "path": "data/input/123456789.jpg"
}
```

### WebSocket Message (Server → Client)
**Type: new_id**
```json
{
  "type": "new_id",
  "student_id": "123456789",
  "front_url": "/output/123456789_FRONT.png",
  "back_url": "/output/123456789_BACK.png"
}
```

---

## ⚡ Quick Start Commands

### First Time Setup
```powershell
# Install frontend dependencies
cd c:\School_IDs\UI
npm install

# Activate Python environment
cd c:\School_IDs
.\venv\Scripts\activate
```

### Development Workflow
```powershell
# Terminal 1: Start Backend
cd c:\School_IDs
.\venv\Scripts\activate
uvicorn app.api:app --reload --port 8000

# Terminal 2: Start Frontend
cd c:\School_IDs\UI
npm run dev

# Access: http://localhost:5173
```

### Production Build
```powershell
# Build React app
cd c:\School_IDs\UI
npm run build

# Start backend (serves React build)
cd c:\School_IDs
.\venv\Scripts\activate
uvicorn app.api:app --port 8000

# Access: http://localhost:8000
```

---

## 📝 Next Steps

1. **Immediate Action Required:**
   - [ ] Update all backend routes to include `/api` prefix
   - [ ] Add DELETE endpoint for template deletion
   - [ ] Remove old HTML file routes from `app/api.py`
   - [ ] Test WebSocket connection with both servers running

2. **Optional Improvements:**
   - [ ] Add environment variables for API URL configuration
   - [ ] Implement backend health check endpoint (`/api/health`)
   - [ ] Add error logging for failed API requests
   - [ ] Set up production deployment configuration
   - [ ] Add authentication/authorization if needed

3. **Cleanup:**
   - [ ] Delete `web/` directory after confirming React UI works
   - [ ] Remove unused dependencies from `requirements.txt`
   - [ ] Update main `README.md` with new architecture

---

## 🆘 Support

**Frontend Issues:**
- Check browser console (F12) for errors
- Review Network tab for failed API requests
- Verify Vite dev server is running on port 5173

**Backend Issues:**
- Check terminal logs for Python errors
- Verify FastAPI server is running on port 8000
- Test API endpoints directly with curl or Postman

**Integration Issues:**
- Ensure both servers are running simultaneously
- Check proxy configuration in `vite.config.js`
- Verify CORS settings in `app/api.py`

---

**Generated for School ID Automation System**  
**Migration Date:** January 5, 2026  
**Migrated From:** Vanilla HTML/JS  
**Migrated To:** React 18.3.1 + Vite 6.0.1 + Tailwind CSS 3.4.15
