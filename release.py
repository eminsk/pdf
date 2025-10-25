#!/usr/bin/env python3
"""
Release script for PDF Viewer
Creates git tags and triggers GitHub Actions build
"""

import sys
import subprocess
import re
from pathlib import Path

def get_current_version():
    """Get current version from pyproject.toml"""
    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        print("❌ pyproject.toml not found")
        sys.exit(1)
    
    content = pyproject.read_text()
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        print("❌ Version not found in pyproject.toml")
        sys.exit(1)
    
    return match.group(1)

def update_version(new_version):
    """Update version in pyproject.toml"""
    pyproject = Path("pyproject.toml")
    content = pyproject.read_text()
    
    # Update version
    content = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content)
    pyproject.write_text(content)
    
    print(f"✅ Updated version to {new_version}")

def run_command(cmd, check=True):
    """Run shell command"""
    print(f"🔄 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"❌ Command failed: {result.stderr}")
        sys.exit(1)
    
    return result

def create_release(version, push=True):
    """Create git tag and push to trigger release"""
    tag = f"v{version}"
    
    # Check if tag already exists
    result = run_command(["git", "tag", "-l", tag], check=False)
    if tag in result.stdout:
        print(f"❌ Tag {tag} already exists")
        sys.exit(1)
    
    # Check for uncommitted changes
    result = run_command(["git", "status", "--porcelain"], check=False)
    if result.stdout.strip():
        print("📝 Uncommitted changes found. Committing...")
        run_command(["git", "add", "."])
        run_command(["git", "commit", "-m", f"Release {tag}"])
    
    # Create and push tag
    run_command(["git", "tag", "-a", tag, "-m", f"Release {tag}"])
    
    if push:
        print(f"🚀 Pushing tag {tag} to trigger release build...")
        run_command(["git", "push", "origin", tag])
        run_command(["git", "push", "origin", "main"])
        
        print(f"""
✅ Release {tag} created successfully!

🔗 Check the build progress at:
   https://github.com/YOUR_USERNAME/pdf-viewer/actions

📦 Release will be available at:
   https://github.com/YOUR_USERNAME/pdf-viewer/releases/tag/{tag}
""")
    else:
        print(f"✅ Tag {tag} created locally. Use 'git push origin {tag}' to trigger release.")

def main():
    if len(sys.argv) < 2:
        current = get_current_version()
        print(f"""
PDF Viewer Release Tool

Current version: {current}

Usage:
  python release.py <version>     # Create release with new version
  python release.py --current     # Create release with current version
  python release.py --local       # Create tag locally without pushing

Examples:
  python release.py 1.0.1
  python release.py --current
""")
        sys.exit(1)
    
    arg = sys.argv[1]
    push = True
    
    if arg == "--current":
        version = get_current_version()
    elif arg == "--local":
        version = get_current_version()
        push = False
    else:
        # Validate version format
        if not re.match(r'^\d+\.\d+\.\d+$', arg):
            print("❌ Version must be in format X.Y.Z (e.g., 1.0.1)")
            sys.exit(1)
        
        version = arg
        update_version(version)
    
    create_release(version, push)

if __name__ == "__main__":
    main()