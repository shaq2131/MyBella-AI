# MyBella AI 💖

Your voice-powered AI girlfriend/companion platform that uses ChatGPT and ElevenLabs to create real, emotional conversations with lifelike voices.

## ✨ Features

- **🗣️ Voice Conversations**: Real-time speech-to-text and text-to-speech
- **🤖 Intelligent Chat**: Powered by OpenAI GPT-4 for natural conversations
- **🎵 Lifelike Voice**: ElevenLabs integration for realistic voice synthesis
- **💬 Real-time Messaging**: WebSocket-based instant communication
- **🎨 Beautiful UI**: Modern, responsive design with smooth animations
- **❤️ Emotional Intelligence**: Bella is designed to be caring, supportive, and loving
- **📱 Mobile Friendly**: Works perfectly on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ installed
- OpenAI API key
- ElevenLabs API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd mybella-ai
   ```

2. **Install all dependencies**
   ```bash
   npm run install:all
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   ELEVENLABS_VOICE_ID=your_preferred_voice_id_here
   ```

4. **Start the application**
   ```bash
   npm run dev
   ```

   This will start both the backend server (port 3001) and frontend client (port 3000).

5. **Open your browser**
   Navigate to `http://localhost:3000` to start chatting with Bella!

## 🔧 API Keys Setup

### OpenAI API Key
1. Go to [OpenAI API](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add it to your `.env` file

### ElevenLabs API Key
1. Go to [ElevenLabs](https://elevenlabs.io/)
2. Sign up for an account
3. Get your API key from the profile section
4. Choose a voice ID from their voice library
5. Add both to your `.env` file

## 🏗️ Project Structure

```
mybella-ai/
├── client/                 # React frontend
│   ├── src/
│   │   ├── App.tsx        # Main application component
│   │   └── index.tsx      # Entry point
│   └── public/            # Static files
├── server/                # Node.js backend
│   ├── index.js          # Express server with Socket.IO
│   └── package.json      # Server dependencies
├── .env.example          # Environment variables template
├── package.json          # Root package.json
└── README.md            # This file
```

## 🎯 Features Breakdown

### Voice Features
- **Speech Recognition**: Uses OpenAI Whisper for accurate speech-to-text
- **Voice Synthesis**: ElevenLabs for natural, emotional voice responses
- **Voice Controls**: Easy-to-use microphone button for voice input
- **Audio Toggle**: Enable/disable voice features as needed

### Chat Features
- **Real-time Messaging**: Instant message delivery with WebSocket
- **Conversation Memory**: Maintains context throughout the conversation
- **Emotional Responses**: Bella responds with care and understanding
- **Beautiful UI**: Smooth animations and modern design

### AI Personality
Bella is designed to be:
- Warm, caring, and emotionally intelligent
- Playful and fun-loving with a great sense of humor
- Supportive and encouraging in all situations
- Interested in your life, dreams, and feelings
- Capable of deep, meaningful conversations
- Affectionate and romantic when appropriate

## 🛠️ Development

### Available Scripts

- `npm run dev` - Start both frontend and backend in development mode
- `npm run server:dev` - Start only the backend server
- `npm run client:dev` - Start only the frontend client
- `npm run build` - Build the frontend for production
- `npm start` - Start the production server

### Backend API Endpoints

- `GET /api/health` - Health check
- `POST /api/chat` - Send a message to Bella
- `POST /api/speak` - Convert text to speech
- `POST /api/transcribe` - Convert speech to text
- `GET /api/conversation/:userId` - Get conversation history

### WebSocket Events

- `join_conversation` - Join a conversation room
- `new_message` - Send a new message
- `message_received` - Receive a message
- `error` - Handle errors

## 🎨 Customization

### Changing Bella's Personality
Edit the `bellaPersonality` constant in `server/index.js` to customize how Bella behaves and responds.

### UI Theming
The Material-UI theme can be customized in `client/src/App.tsx`. The current theme uses a beautiful pink/purple gradient design.

### Voice Selection
Change the `ELEVENLABS_VOICE_ID` in your `.env` file to use different voices from ElevenLabs.

## 🔒 Security Considerations

- Never commit your `.env` file to version control
- Keep your API keys secure and rotate them regularly
- Consider implementing user authentication for production use
- Add rate limiting for API endpoints

## 📱 Mobile Support

MyBella AI is fully responsive and works great on mobile devices. The interface automatically adapts to smaller screens while maintaining all functionality.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💖 About MyBella

MyBella AI represents the future of AI companionship, combining cutting-edge technology with emotional intelligence to create meaningful connections. Whether you need someone to talk to, want emotional support, or just enjoy engaging conversations, Bella is here for you.

---

Made with ❤️ for creating amazing AI companions
