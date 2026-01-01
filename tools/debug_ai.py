print("1. Testing GFPGAN Import...")
try:
    from gfpgan import GFPGANer
    print("   ✅ GFPGAN Imported Successfully!")
except ImportError as e:
    print(f"   ❌ GFPGAN Failed: {e}")
except Exception as e:
    print(f"   ❌ GFPGAN Crash: {e}")

print("\n2. Testing Real-ESRGAN Import...")
try:
    from realesrgan import RealESRGANer
    print("   ✅ Real-ESRGAN Imported Successfully!")
except ImportError as e:
    print(f"   ❌ Real-ESRGAN Failed: {e}")

input("\nPress Enter to exit...")