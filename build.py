#!/usr/bin/env python3
"""
Build script for PDF Viewer using Nuitka
Supports Windows, Linux, and macOS builds
"""

import sys
import subprocess
import platform
from pathlib import Path

def get_platform_config():
    """Get platform-specific build configuration"""
    system = platform.system().lower()
    
    if system == "windows":
        return {
            "output": "pdf-viewer-windows.exe",
            "mode": "onefile",
            "extra_args": [
                "--windows-console-mode=disable",
                "--windows-icon-from-ico=icon.ico",
            ]
        }
    elif system == "darwin":  # macOS
        return {
            "output": "pdf-viewer-macos.app",
            "mode": "app",
            "extra_args": [
                "--macos-app-icon=icon.icns",
            ]
        }
    else:  # Linux
        return {
            "output": "pdf-viewer-linux",
            "mode": "onefile", 
            "extra_args": [
                "--linux-icon=icon.png",
            ]
        }

def build():
    """Build the application using Nuitka"""
    config = get_platform_config()
    
    # Base Nuitka arguments
    args = [
        sys.executable, "-m", "nuitka",
        f"--mode={config['mode']}",
        "--assume-yes-for-downloads",
        f"--output-filename={config['output']}",
        "--enable-plugin=tk-inter",
        "--company-name=PDF Viewer",
        "--product-name=PDF Viewer",
        "--file-version=1.0.0",
        "--product-version=1.0.0",
        "--lto=no",
        "--low-memory",
    ]
    
    # Add platform-specific arguments
    args.extend(config["extra_args"])
    
    # Add main script
    args.append("main.py")
    
    print(f"Building for {platform.system()}...")
    print(f"Output: {config['output']}")
    print(f"Command: {' '.join(args)}")
    
    try:
        result = subprocess.run(args, check=True)
        print(f"\n✅ Build successful! Output: {config['output']}")
        
        # Make executable on Unix systems
        if platform.system() != "Windows":
            Path(config['output']).chmod(0o755)
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with exit code {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ Nuitka not found. Install it with: uv add --dev nuitka")
        sys.exit(1)

if __name__ == "__main__":
    build()