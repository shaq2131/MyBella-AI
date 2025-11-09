#!/usr/bin/env python3
"""
MyBella Setup Script
Installs dependencies and sets up the environment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Starting {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"{description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_directories():
    """Create necessary directories in your existing structure"""
    # Get the project root (3 levels up from this script)
    project_root = Path(__file__).parent.parent.parent.parent
    
    directories = [
        project_root / "backend" / "database" / "instances" / "uploads",
        project_root / "backend" / "database" / "instances" / "uploads" / "profile_pics", 
        project_root / "backend" / "database" / "instances" / "uploads" / "persona_pics",
        project_root / "logs"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    print(f"Created directory: {directory}")

def install_requirements():
    """Install Python requirements"""
    # Get the project root to find requirements files
    project_root = Path(__file__).parent.parent.parent.parent
    requirements_files = [
        project_root / "requirements-minimal.txt", 
        project_root / "requirements.txt"
    ]
    
    for req_file in requirements_files:
        if req_file.exists():
            print(f"Installing dependencies from {req_file.name}")
            success = run_command(f"pip install -r {req_file}", f"Installing {req_file.name}")
            if success:
                return True
            else:
                print(f"Failed to install from {req_file.name}, trying next...")

    print("No requirements file found or all installations failed")
    return False

def setup_environment():
    """Set up environment variables"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("Created .env file from .env.example")
        else:
            print("No .env.example found; create .env manually")
    else:
        print(".env file already exists")

def display_next_steps():
    """Display next steps for the user"""
    print("\nSetup completed! Next steps:")
    print("\n1. Configure your API keys in the .env file:")
    print("   - Add your OpenAI API key for AI chat")
    print("   - Add your ElevenLabs API key for voice synthesis")
    print("   - (Optional) Add Firebase and Pinecone keys for enhanced features")
    
    print("\n2. Run the application:")
    print("   python mybella.py")
    
    print("\n3. Open your browser and go to:")
    print("   http://127.0.0.1:5000")
    
    print("\nDocumentation:")
    print("   - OpenAI API: https://platform.openai.com/api-keys")
    print("   - ElevenLabs API: https://elevenlabs.io/")
    print("   - Firebase: https://console.firebase.google.com/")
    print("   - Pinecone: https://www.pinecone.io/")

def main():
    """Main setup function"""
    print("MyBella Setup Starting...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    print("\nCreating directories...")
    create_directories()
    
    # Install requirements
    print("\nInstalling dependencies...")
    if not install_requirements():
        print("Dependency installation failed, but you can try manually:")
        print("   pip install -r requirements-minimal.txt")
    
    # Setup environment
    print("\nSetting up environment...")
    setup_environment()
    
    # Display next steps
    display_next_steps()
    
    print("\nSetup complete. Happy coding!")

if __name__ == "__main__":
    main()