# MyBella Setup Scripts

This folder contains setup scripts to configure your MyBella development environment.

## 📋 Available Scripts

### 🐍 Python Setup (setup.py)
Comprehensive setup script that handles all dependencies and configuration.

**Usage:**
```bash
# From project root
python backend/scripts/setup/setup.py
```

**Features:**
- ✅ Python version validation (3.8+)
- ✅ Creates necessary directories
- ✅ Installs Python dependencies
- ✅ Creates .env configuration file
- ✅ Initializes database
- ✅ Validates installation

### 💙 PowerShell Setup (setup.ps1)
Windows-specific setup script with enhanced PowerShell support.

**Usage:**
```powershell
# From project root
.\backend\scripts\setup\setup.ps1
```

**Features:**
- ✅ Python installation check
- ✅ Virtual environment creation
- ✅ Directory structure setup
- ✅ Dependency installation
- ✅ Environment configuration
- ✅ Database initialization

## 🚀 Quick Start

1. **Clone the repository**
2. **Navigate to project root** (`MYBELLA/`)
3. **Run setup script:**
   - **Python:** `python backend/scripts/setup/setup.py`
   - **PowerShell:** `.\backend\scripts\setup\setup.ps1`
4. **Follow the prompts** and provide API keys when requested
5. **Start the application** with `python mybella.py`

## 📁 Directory Structure Created

```
backend/database/instances/
├── mybella.db                    # SQLite database
└── uploads/                      # File uploads
    ├── profile_pics/             # User profile pictures  
    └── persona_pics/             # AI persona avatars
```

## 🔑 Environment Configuration

The setup scripts will create a `.env` file with the following variables:

```env
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key
FLASK_ENV=development

# API Keys (you'll be prompted to enter these)
OPENAI_API_KEY=your-openai-key
ELEVENLABS_API_KEY=your-elevenlabs-key
ELEVENLABS_VOICE_ID=default-voice-id

# Optional Services
FIREBASE_PROJECT_ID=your-firebase-project
PINECONE_API_KEY=your-pinecone-key
```

## 🛠️ Manual Setup

If you prefer manual setup:

1. **Create directories:**
   ```bash
   mkdir -p backend/database/instances/uploads/{profile_pics,persona_pics}
   mkdir -p logs
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create .env file** with your API keys

4. **Initialize database:**
   ```bash
   python -c "from backend import create_app; app, _ = create_app()"
   ```

## 📞 Support

If you encounter issues:
- Check Python version (3.8+ required)
- Ensure pip is updated: `python -m pip install --upgrade pip`
- Verify API keys are valid
- Check file permissions for directory creation

Happy coding! 🎉