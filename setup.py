#!/usr/bin/env python3
"""
MyBella Quick Setup Launcher
Runs the setup script from the scripts folder
"""

import os
import sys
from pathlib import Path

def main():
    """Run the setup script from the scripts folder"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    setup_script = project_root / "backend" / "scripts" / "setup" / "setup.py"
    
    # Check if setup script exists
    if not setup_script.exists():
        print("❌ Setup script not found at:", setup_script)
        sys.exit(1)
    
    print("🚀 Launching MyBella setup...")
    print(f"📁 Running setup from: {setup_script}")
    print()
    
    # Import and run the setup
    import subprocess
    result = subprocess.run([sys.executable, str(setup_script)], cwd=project_root)
    
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()