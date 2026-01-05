# School ID Card Generation System

**Modern React + FastAPI application** that generates ID card images (front/back PNG) from captured photos and student metadata.

## 🎯 System Overview

This system consists of two integrated components:
- **Backend:** Python FastAPI server with AI-powered image enhancement
- **Frontend:** React 18 SPA with Vite, Tailwind CSS, and real-time WebSocket updates

## 📚 Documentation

- **[Integration Guide](INTEGRATION_GUIDE.md)** — **START HERE** - Complete backend-frontend setup
- **[Frontend README](UI/README.md)** — React app documentation
- **[Technical Documentation](documentation/TECHNICAL_DOCS.md)** — For developers and IT staff
- **[User Manual](documentation/USER_MANUAL.md)** — For operators

---

## ⚡ Quick Start (Automated)

**Easiest way to start the entire system:**

```powershell
.\START_SYSTEM.ps1
```

This script will:
1. Start the Python FastAPI backend on port 8000
2. Start the React frontend on port 5173
3. Open your browser to http://localhost:5173

---

## 📋 Manual Setup

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** (for React frontend)
- **MySQL Server**
- **Camera device** (for capture station)

### Backend Installation

1. Create virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install Python dependencies:
```powershell
pip install -r requirement.txt
```

3. Configure database (optional - uses environment variables):
```powershell
$env:DB_HOST="localhost"
$env:DB_USER="root"
$env:DB_PASSWORD="your_password"
$env:DB_NAME="school_id_system"
```

4. Initialize database:
```powershell
python -c "from app.database import init_db; init_db()"
```

### Frontend Installation

1. Navigate to UI directory:
```powershell
cd UI
```

2. Install Node dependencies:
```powershell
npm install
```

### Running the System

**Option 1: Using the startup script (Recommended)**
```powershell
.\START_SYSTEM.ps1
```

**Option 2: Manual (Two separate terminals)**

Terminal 1 - Backend:
```powershell
.\venv\Scripts\Activate.ps1
uvicorn app.api:app --reload --port 8000
```

Terminal 2 - Frontend:
```powershell
cd UI
npm run dev
```

Access the application at: **http://localhost:5173**

---

## 🏗️ System Architecture

### Frontend (React SPA)
- **Framework:** React 18.3.1 with React Router 6
- **Build Tool:** Vite 6.0.1 with HMR
- **Styling:** Tailwind CSS 3.4.15 with custom navy design system
- **Icons:** Phosphor Icons 2.1.7
- **State:** Context API (WebSocket, Toast, Settings)
- **Dev Server:** http://localhost:5173
- **Location:** `UI/` directory

### Backend (Python API)
- **Framework:** FastAPI with WebSocket support
- **Image Processing:** Pillow, OpenCV, GFPGAN (optional)
- **Database:** MySQL with `mysql-connector-python`
- **File Watching:** Watchdog for auto-processing
- **Server:** http://localhost:8000
- **Location:** `app/` directory

### Integration
- **API Proxy:** Vite proxies `/api/*` to backend
- **WebSocket:** Real-time updates for ID generation
- **CORS:** Enabled for local development

---

## ✨ Key Features

### 📸 Capture Station
- Live camera preview with alignment guide
- Database lookup or manual student entry
- Recent captures with thumbnails
- WebSocket notifications on completion

### 📊 Dashboard
- Template management (upload/select/delete)
- Student database with search/filter
- Latest generated ID preview
- Edit student records
- Regenerate IDs with one click

### 🎨 Layout Editor
- Visual drag-and-drop element positioning
- Front/back template switching
- Layer visibility controls
- Property panel (position, size, typography)
- Real-time canvas preview with zoom

### ⚙️ Settings
- AI enhancement controls (strength slider)
- Feature toggles (face restoration, hair cleanup, background removal)
- System monitoring (storage, queue, database)
- Clear history and export analytics

---

## 📂 Project Structure

```
School_IDs/
├── app/                          # Backend (Python FastAPI)
│   ├── api.py                   # API routes + WebSocket
│   ├── school_id_processor.py   # Image processing pipeline
│   ├── database.py              # MySQL integration
│   ├── glam_engine.py           # AI enhancement (GFPGAN)
│   └── batch_printer.py         # Batch processing
├── UI/                          # Frontend (React + Vite)
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── capture/       # Capture Station page
│   │   │   ├── dashboard/     # Dashboard page
│   │   │   ├── editor/        # Layout Editor page
│   │   │   ├── layout/        # Sidebar navigation
│   │   │   └── shared/        # Reusable UI components
│   │   ├── contexts/          # Global state (WebSocket, Toast, Settings)
│   │   ├── hooks/             # Custom hooks (useStudents, useHistory, etc.)
│   │   ├── utils/             # Helper functions
│   │   ├── App.jsx            # Root component with routing
│   │   └── main.jsx           # Entry point
│   ├── public/                # Static assets
│   ├── package.json           # Node dependencies
│   ├── vite.config.js         # Dev server + proxy
│   └── tailwind.config.js     # Design system
├── data/
│   ├── input/                 # Captured photos (trigger processing)
│   ├── output/                # Generated ID cards
│   ├── templates/             # Template background images
│   ├── layout.json            # Field positioning config
│   └── settings.json          # Active templates and enhancement options
├── gfpgan/                    # AI enhancement models
│   └── weights/              # Pre-trained model weights
├── documentation/             # Technical docs and user manuals
├── tools/                     # Admin and utility scripts
├── venv/                      # Python virtual environment
├── START_SYSTEM.ps1          # 🚀 One-click startup script
├── INTEGRATION_GUIDE.md      # Backend-frontend integration guide
└── README.md                 # This file
```

---

## 🔌 API Endpoints

All endpoints are prefixed with `/api`:

### Settings
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Save settings

### Students
- `GET /api/students` - Get all students
- `POST /api/students/update` - Update student record

### Templates
- `GET /api/templates/list` - List available templates
- `POST /api/templates/upload` - Upload new template
- `DELETE /api/templates/{filename}` - Delete template

### Layout
- `GET /api/layout` - Get layout configuration
- `POST /api/layout` - Save layout configuration

### Capture & Processing
- `POST /api/capture` - Upload photo and trigger processing
- `POST /api/regenerate/{student_id}` - Regenerate ID for student

### History
- `GET /api/history` - Get generation history

### WebSocket
- `ws://localhost:8000/ws` - Real-time updates

---

## 🎨 Design System

### Color Palette
The UI uses a custom navy theme:
- **navy-950:** `#0a0e1f` (Main background)
- **navy-900:** `#0f1729` (Cards, panels)
- **navy-800:** `#1a2235` (Elevated elements)
- **navy-700:** `#242d42` (Borders)

### Typography
- **UI Font:** Inter (Google Fonts)
- **Code Font:** JetBrains Mono

### Components
50+ reusable React components including:
- Button (4 variants, 3 sizes)
- Input with validation states
- Modal with 5 sizes
- Toast notifications
- Dropdown with search
- Toggle switches
- Sliders
- And more...

---

## 🛠️ Development Tools

### Available Scripts

**Backend:**
```powershell
# Run with auto-reload
uvicorn app.api:app --reload --port 8000

# Run tests
python -m pytest tests/

# Initialize database
python -c "from app.database import init_db; init_db()"
```

**Frontend:**
```powershell
cd UI

# Development server with HMR
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Environment Variables

**Backend:**
```powershell
$env:DB_HOST="localhost"
$env:DB_USER="root"
$env:DB_PASSWORD="your_password"
$env:DB_NAME="school_id_system"
```

---

## 📖 Configuration Files

### Backend: `data/settings.json`
```json
{
  "active_template_front": "TEMPLATE_FRONT.png",
  "active_template_back": "TEMPLATE_BACK.png",
  "smooth_strength": 5,
  "enable_face_restoration": true,
  "enable_hair_cleanup": false,
  "enable_bg_removal": false
}
```

### Backend: `data/layout.json`
```json
{
  "front": {
    "elements": [
      {
        "id": "photo",
        "type": "photo",
        "x": 63,
        "y": 201,
        "width": 465,
        "height": 465
      },
      {
        "id": "name",
        "type": "text",
        "x": 297,
        "y": 682,
        "fontSize": 30,
        "color": "#000000",
        "fontWeight": "bold"
      }
    ]
  },
  "back": {
    "elements": []
  }
}
```

### Frontend: `UI/vite.config.js`
```javascript
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})
```

---

## 🚨 Troubleshooting

### "WebSocket connection error"
**Solution:** Ensure backend server is running on port 8000
```powershell
uvicorn app.api:app --reload --port 8000
```

### "Failed to fetch settings"
**Solution:** Backend API routes must include `/api` prefix (see [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md))

### "Camera not detected"
**Solution:** Allow camera permissions in browser settings

### "Module not found" errors
**Solution:** Install dependencies
```powershell
# Backend
pip install -r requirement.txt

# Frontend
cd UI
npm install
```

For detailed troubleshooting, see [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)

---

## 🔐 Production Deployment Checklist

Before deploying to production:

- [ ] **Authentication:** Implement user authentication and role-based access
- [ ] **CORS:** Restrict allowed origins in FastAPI CORS middleware
- [ ] **HTTPS:** Use SSL/TLS certificates for secure connections
- [ ] **Environment:** Use environment variables for sensitive data
- [ ] **Database:** Use proper database credentials and connection pooling
- [ ] **Build:** Create production build of React app (`npm run build`)
- [ ] **Reverse Proxy:** Use Nginx or similar for serving static files
- [ ] **Monitoring:** Add logging, error tracking, and health checks
- [ ] **Backups:** Implement regular database and file backups
- [ ] **Rate Limiting:** Protect API endpoints from abuse

---

## 📚 Additional Resources

- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Complete backend-frontend setup guide
- **[UI/README.md](UI/README.md)** - React app documentation with component library
- **[documentation/TECHNICAL_DOCS.md](documentation/TECHNICAL_DOCS.md)** - Architecture deep dive
- **[documentation/USER_MANUAL.md](documentation/USER_MANUAL.md)** - End-user documentation

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

(Add your license information here)
