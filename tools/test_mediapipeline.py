try:
    import mediapipe as mp
    if hasattr(mp, 'solutions'):
        print("✅ SUCCESS: MediaPipe is working!")
        print(f"   - Face Mesh Available: {hasattr(mp.solutions, 'face_mesh')}")
    else:
        print("❌ ERROR: MediaPipe installed, but 'solutions' is still missing.")
except ImportError:
    print("❌ ERROR: MediaPipe is not installed.")