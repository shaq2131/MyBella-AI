# MyBella - AI Companion Application

A sophisticated AI companion application with real-time chat, voice chat, and subscription management. Features include AI-powered conversations with OpenAI, voice synthesis with ElevenLabs, real-time communication with Socket.IO, and profile picture support.

## � Project Structure

```
MYBELLA/
├── mybella.py                    # Main application entry point
├── setup.py                     # Quick setup launcher
├── setup.ps1                    # PowerShell setup launcher
├── requirements.txt             # Python dependencies
├── requirements-minimal.txt     # Minimal dependencies
├── .env                         # Environment variables (create from .env.example)
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore patterns
├── README.md                    # This file
│
├── backend/                     # Backend application
│   ├── __init__.py             # Flask app factory
│   ├── database/               # Database layer
│   │   ├── models/
│   │   │   └── models.py       # SQLAlchemy models
│   │   ├── utils/
│   │   │   └── utils.py        # Database utilities
│   │   └── instances/          # Database files and uploads
│   │       ├── mybella.db      # SQLite database
│   │       └── uploads/        # File uploads
│   │           ├── profile_pics/
│   │           └── persona_pics/
│   │
│   ├── funcs/                  # CRUD functions
│   │   ├── users/              # User operations
│   │   ├── admin/              # Admin operations
│   │   ├── personas/           # Persona management
│   │   └── voice/              # Voice chat operations
│   │
│   ├── routes/                 # Flask routes
│   │   ├── auth/               # Authentication routes
│   │   │   ├── users/          # User authentication
│   │   │   └── admin/          # Admin authentication
│   │   ├── views/              # HTML view routes
│   │   │   ├── users/          # User dashboard/profile
│   │   │   ├── admin/          # Admin panel
│   │   │   └── main_routes.py  # Main navigation
│   │   └── api/                # API endpoints
│   │       └── chat_routes.py  # Chat, voice, and profile APIs
│   │
│   ├── services/               # External services
│   │   ├── config.py           # Application configuration
│   │   ├── socketio/           # Real-time communication
│   │   ├── voice/              # Voice chat service
│   │   ├── chat/               # AI chat service
│   │   ├── elevenlabs/         # Text-to-speech
│   │   ├── firebase/           # Firebase integration
│   │   └── pinecone/           # Vector database
│   │
│   └── scripts/                # Utility scripts
│       ├── setup/              # Setup and installation
│       │   ├── setup.py        # Python setup script
│       │   ├── setup.ps1       # PowerShell setup script
│       │   └── README.md       # Setup documentation
│       ├── seeds/              # Database seeding
│       └── test/               # Test scripts
│
└── frontend/                   # Frontend assets
    ├── static/                 # Static files (CSS, JS, images)
    │   ├── css/
    │   ├── js/
    │   └── img/
    └── templates/              # Jinja2 HTML templates
```

## �🚀 Features

- **AI Chat**: OpenAI GPT-4 powered conversations with multiple personas
- **Voice Chat**: Real-time voice conversations with AI personas using ElevenLabs TTS
- **Real-time Communication**: Socket.IO for live chat and voice updates
- **Profile Pictures**: Upload and manage user and persona avatars
- **Subscription System**: Minute-based voice chat plans
- **Multiple Personas**: Isabella, Alex, Luna, Maya with unique personalities
- **Conversation Modes**: Companion, Wellness, and more
- **Memory System**: Pinecone vector database for conversation history
- **Secure Authentication**: User accounts with role-based access

## 📋 Requirements

- Python 3.8 or higher
- OpenAI API key (for AI chat)
- ElevenLabs API key (for voice synthesis)
- Optional: Firebase (for enhanced features)
- Optional: Pinecone (for conversation memory)

## 🛠️ Quick Setup

### Option 1: Automated Setup (Recommended)

**For Windows PowerShell:**
```powershell
.\setup.ps1
```

**For Python:**
```bash
python setup.py
```

### Option 2: Manual Setup

1. **Clone and navigate to the project:**
   ```bash
   cd MYBELLA
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements-minimal.txt
   # Or for full features:
   pip install -r requirements.txt
   ```

4. **Create directories:**
   ```bash
   mkdir -p instance/uploads/profile_pics
   mkdir -p instance/uploads/persona_pics
   mkdir -p logs
   ```

5. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys
   ```

## 🔑 Environment Configuration

Edit the `.env` file with your API keys:

```env
# Required: OpenAI API (Get from: https://platform.openai.com/api-keys)
OPENAI_API_KEY=your_openai_api_key_here

# Required: ElevenLabs API (Get from: https://elevenlabs.io/)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Optional: Firebase (Get from: https://console.firebase.google.com/)
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_CLIENT_EMAIL=your_firebase_client_email
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour_key_here\n-----END PRIVATE KEY-----"

# Optional: Pinecone (Get from: https://www.pinecone.io/)
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX=mybella-memory
```

## ▶️ Running the Application

1. **Start the server:**
   ```bash
   python mybella.py
   ```

2. **Open your browser:**
   ```
   http://127.0.0.1:5000
   ```

3. **Create an account and start chatting!**

## 🏗️ Architecture

### Backend Components
- **Flask**: Web framework with SQLAlchemy ORM
- **Socket.IO**: Real-time communication
- **OpenAI**: AI chat responses
- **ElevenLabs**: Text-to-speech synthesis
- **SQLite**: Database for users, chats, voice chats
- **Firebase**: Optional cloud storage
- **Pinecone**: Optional vector database for memory

### Frontend Components
- **HTML/CSS/JavaScript**: Responsive web interface
- **Socket.IO Client**: Real-time updates
- **Bootstrap**: UI components
- **Audio API**: Voice playback

### Key Features
- **Voice Chat**: Real-time AI conversation with TTS
- **Chat System**: WebSocket-based messaging
- **Profile Management**: User and persona avatars
- **Subscription System**: Minute-based voice chat
- **Admin Panel**: User and system management

## 📁 Project Structure

```
MYBELLA/
├── backend/                 # Backend application
│   ├── database/           # Database models and utils
│   ├── funcs/              # CRUD operations
│   ├── routes/             # API and view routes
│   └── services/           # External service integrations
├── frontend/               # Frontend assets
│   ├── static/            # CSS, JS, images
│   └── templates/         # HTML templates
├── instance/              # Instance-specific files
│   ├── uploads/          # User uploads
│   └── mybella.db        # SQLite database
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
└── mybella.py            # Application entry point
```

## 🔧 API Endpoints

### Chat & TTS
- `POST /api/chat` - Send message and get AI response
- `POST /api/tts` - Generate text-to-speech audio
- `POST /api/voice-upload` - Upload custom voice

### Voice Chat
- `GET /api/voice/eligibility` - Check call eligibility
- `POST /api/voice/call/initiate` - Start voice chat
- `POST /api/voice/call/start/<id>` - Begin call session
- `POST /api/voice/call/end/<id>` - End voice chat
- `POST /api/voice/session/speech` - Process speech input

### Profile Management
- `POST /api/profile-picture` - Upload user profile picture
- `POST /api/persona-picture` - Upload persona avatar

### Subscription
- `GET /api/subscription/plans` - Get available plans
- `POST /subscription/upgrade` - Upgrade subscription

## 🎭 Personas

- **Isabella**: Warm, empathetic companion for emotional support
- **Alex**: Friendly, knowledgeable assistant for productivity
- **Luna**: Creative, artistic companion for arts and literature
- **Maya**: Wellness-focused companion for mindfulness and self-care

Each persona has:
- Unique personality and conversation style
- Custom voice via ElevenLabs
- Profile picture support
- Specialized conversation modes

## 🔒 Security Features

- User authentication with Flask-Login
- Secure file upload validation
- Session management
- CSRF protection
- Input sanitization
- Role-based access control

## 🚀 Production Deployment

1. **Set environment to production:**
   ```env
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

2. **Use production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -k eventlet mybella:app
   ```

3. **Configure reverse proxy (nginx/Apache)**

4. **Set up SSL certificates**

5. **Configure database (PostgreSQL recommended for production)**

## 🐛 Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed
2. **API key errors**: Check .env file configuration
3. **Database errors**: Delete instance/mybella.db to reset
4. **Socket.IO connection**: Check firewall and CORS settings
5. **Voice synthesis fails**: Verify ElevenLabs API key and credits

### Debug Mode
Set `FLASK_DEBUG=True` in .env for detailed error messages.

### Logs
Check `logs/mybella.log` for application logs.

## 📚 Documentation

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [ElevenLabs API Documentation](https://docs.elevenlabs.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Socket.IO Documentation](https://socket.io/docs/)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for providing powerful AI capabilities
- ElevenLabs for high-quality voice synthesis
- Flask community for excellent web framework
- Socket.IO team for real-time communication

## 📞 Support

For support, email support@mybella.app or create an issue in the repository.

---

**Happy coding! 🎉**