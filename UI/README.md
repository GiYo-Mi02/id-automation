# ID Automation System - React Frontend

Modern React frontend for the ID Automation System built with Vite, Tailwind CSS, and Phosphor Icons.

## Features

- **Capture Station** - Real-time camera capture with student search
- **Dashboard** - View generated IDs, manage templates, edit student data
- **Layout Editor** - Visual drag-and-drop editor for ID card layouts
- **Settings** - Configure image enhancement and system preferences

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router 6** - Client-side routing
- **Tailwind CSS** - Utility-first styling
- **Phosphor Icons** - Icon library
- **WebSocket** - Real-time updates

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or pnpm

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### API Proxy

The dev server proxies API requests to the backend:
- `/api/*` → `http://localhost:8000/api/*`
- `/ws` → `ws://localhost:8000/ws`

Make sure the Python backend is running on port 8000.

### Build for Production

```bash
npm run build
```

Output will be in the `dist/` folder.

## Project Structure

```
src/
├── components/
│   ├── capture/       # Capture page components
│   ├── dashboard/     # Dashboard page components
│   ├── editor/        # Layout editor components
│   ├── layout/        # App layout (sidebar)
│   ├── shared/        # Reusable UI components
│   └── utils/         # Utility functions
├── contexts/          # React contexts
├── hooks/             # Custom hooks
├── layouts/           # Page layouts
├── pages/             # Route pages
├── App.jsx            # Root component
├── main.jsx           # Entry point
└── index.css          # Global styles
```

## Design System

### Colors (Navy Theme)

- `navy-950` - Main background (#0a0e1f)
- `navy-900` - Cards/surfaces (#141827)
- `navy-800` - Elevated surfaces (#1e2538)
- `navy-700` - Borders (#2a3147)
- `blue-600` - Primary accent (#2563eb)
- `green-500` - Success (#22c55e)
- `red-500` - Error (#ef4444)

### Components

Shared components are in `src/components/shared/`:

- `Button` - Primary, secondary, ghost, danger variants
- `Input` - Text input with label, error, icon support
- `Modal` - Dialog with header, body, footer
- `Toast` - Notification system
- `Dropdown` - Select component
- `Toggle` - Switch component
- `Slider` - Range input
- `Card` - Container component
- `Badge` - Status indicators
- `Spinner` - Loading indicator

## License

MIT
