import sys
import os
import traceback

# Add the current directory to sys.path so we can import backend
sys.path.append(os.getcwd())

try:
    print(f"Executable: {sys.executable}")
    print(f"Path: {sys.path}")
    print("Attempting to import backend.routes.auth...")
    import backend.routes.auth
    print("Successfully imported backend.routes.auth")
except Exception:
    print("Failed to import backend.routes.auth")
    traceback.print_exc()
