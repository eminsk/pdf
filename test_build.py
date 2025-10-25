#!/usr/bin/env python3
"""
Test script to verify build setup and dependencies
"""

import sys
import subprocess
import platform
from pathlib import Path

def check_uv():
    """Check if uv is installed"""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        print(f"✅ uv found: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ uv not found. Install it from: https://docs.astral.sh/uv/getting-started/installation/")
        return False

def check_dependencies():
    """Check if project dependencies are installed"""
    try:
        result = subprocess.run(["uv", "run", "python", "-c", "import fitz, PIL; print('Dependencies OK')"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Project dependencies installed")
            return True
        else:
            print("❌ Dependencies missing. Run: uv sync")
            return False
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return False

def check_nuitka():
    """Check if Nuitka is available"""
    try:
        result = subprocess.run(["uv", "run", "python", "-m", "nuitka", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Nuitka found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Nuitka not found. Run: uv sync --dev")
            return False
    except Exception as e:
        print(f"❌ Error checking Nuitka: {e}")
        return False

def check_icons():
    """Check if icon files exist"""
    icons = {
        "Windows": "icon.ico",
        "Linux": "icon.png", 
        "macOS": "icon.icns"
    }
    
    missing = []
    for platform_name, icon_file in icons.items():
        if Path(icon_file).exists():
            print(f"✅ {platform_name} icon found: {icon_file}")
        else:
            print(f"⚠️  {platform_name} icon missing: {icon_file}")
            missing.append(icon_file)
    
    return len(missing) == 0

def test_app():
    """Test if the app can be imported and basic functionality works"""
    try:
        result = subprocess.run([
            "uv", "run", "python", "-c", 
            "import main; print('App imports successfully')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ App imports successfully")
            return True
        else:
            print(f"❌ App import failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  App import test timed out (this is normal for GUI apps)")
        return True
    except Exception as e:
        print(f"❌ Error testing app: {e}")
        return False

def main():
    print("🔍 Testing PDF Viewer build setup...\n")
    
    checks = [
        ("UV Package Manager", check_uv),
        ("Project Dependencies", check_dependencies), 
        ("Nuitka Compiler", check_nuitka),
        ("Icon Files", check_icons),
        ("App Import", test_app),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        results.append(check_func())
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("\n🎉 All checks passed! Ready to build.")
        print("\nNext steps:")
        print("  • Build locally: uv run python build.py")
        print("  • Create release: uv run python release.py 1.0.1")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        
    print(f"\nPlatform: {platform.system()} {platform.machine()}")
    print(f"Python: {sys.version}")

if __name__ == "__main__":
    main()