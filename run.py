import uvicorn
import os

if __name__ == "__main__":
    print("🚀 SCHOOL ID SYSTEM STARTING...")
    print("   👉 Dashboard: http://localhost:8000")
    print("   📚 API Docs:  http://localhost:8000/docs")
    
    # Use the new modular entrypoint
    # Falls back to app.api:app for legacy compatibility
    entrypoint = os.environ.get("APP_ENTRYPOINT", "app.main:app")
    uvicorn.run(entrypoint, host="0.0.0.0", port=8000, reload=True)