import sys
import importlib
import traceback

sys.path.insert(0, r'c:\Users\Harsh\Desktop\travel\AI4')

print("Testing auth module import...")
try:
    mod = importlib.import_module("backend.routes.auth")
    print(f"✓ Module imported successfully")
    print(f"✓ Has router: {hasattr(mod, 'router')}")
    if hasattr(mod, 'router'):
        print(f"✓ Router type: {type(mod.router)}")
        print(f"✓ Router routes: {len(mod.router.routes)} routes")
        for route in mod.router.routes:
            print(f"  - {route.path} [{','.join(route.methods) if hasattr(route, 'methods') else 'N/A'}]")
except Exception as e:
    print(f"✗ FAILED: {e}")
    traceback.print_exc()
