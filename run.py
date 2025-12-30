import uvicorn
import os

if __name__ == "__main__":
    print("🚀 RIMBERIO SYSTEM STARTING...")
    print("   👉 Dashboard: http://localhost:8000/dashboard")
    
    # This tells Python to run the app inside the 'app' folder
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)