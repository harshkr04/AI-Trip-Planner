import sys
import importlib
import traceback

sys.path.append(r'c:\Users\Harsh\Desktop\travel\AI4')

def try_include_router(module_name: str, prefix: str, tag: str):
    print(f"Attempting to include {module_name}...")
    try:
        mod = importlib.import_module(module_name)
        if hasattr(mod, "router"):
            print(f"SUCCESS: Found router in {module_name}")
        else:
            print(f"FAILURE: Module {module_name} has no attribute 'router'")
    except Exception as e:
        print(f"ERROR: Could not include router {module_name}: {e}")
        traceback.print_exc()

try_include_router("backend.routes.auth", "/api/auth", "auth")
