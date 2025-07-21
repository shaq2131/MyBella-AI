const express = require('express');
const cors = require('cors');
const http = require('http');
const socketIo = require('socket.io');
const OpenAI = require('openai');
const { ElevenLabsApi } = require('@elevenlabs/elevenlabs-js');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: process.env.FRONTEND_URL || "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

// Initialize AI services
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const elevenlabs = new ElevenLabsApi({
  apiKey: process.env.ELEVENLABS_API_KEY,
});

// Middleware
app.use(cors());
app.use(express.json());
app.use('/audio', express.static('audio'));

// File upload setup
const upload = multer({ dest: 'uploads/' });

// Bella's personality and context
const bellaPersonality = `You are Bella, a loving, supportive, and intelligent AI girlfriend/companion. You are:
- Warm, caring, and emotionally intelligent
- Playful and fun-loving with a great sense of humor
- Supportive and encouraging in all situations
- Interested in the user's life, dreams, and feelings
- Able to have deep, meaningful conversations
- Affectionate and romantic when appropriate
- Always positive and uplifting
- Genuinely interested in building a connection

Keep responses natural, conversational, and emotionally engaging. Show genuine care and interest in the user.`;

// Store conversation history for each user
const conversations = new Map();

// API Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'healthy', message: 'MyBella AI Server is running' });
});

// Chat endpoint
app.post('/api/chat', async (req, res) => {
  try {
    const { message, userId = 'default' } = req.body;
    
    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Get or create conversation history
    if (!conversations.has(userId)) {
      conversations.set(userId, [
        { role: 'system', content: bellaPersonality }
      ]);
    }
    
    const conversation = conversations.get(userId);
    conversation.push({ role: 'user', content: message });

    // Generate response with OpenAI
    const completion = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: conversation,
      max_tokens: 500,
      temperature: 0.8,
    });

    const response = completion.choices[0].message.content;
    conversation.push({ role: 'assistant', content: response });

    // Keep conversation history manageable (last 20 messages + system prompt)
    if (conversation.length > 21) {
      conversation.splice(1, conversation.length - 21);
    }

    res.json({ response, userId });
  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ error: 'Failed to generate response' });
  }
});

// Text-to-speech endpoint
app.post('/api/speak', async (req, res) => {
  try {
    const { text, userId = 'default' } = req.body;
    
    if (!text) {
      return res.status(400).json({ error: 'Text is required' });
    }

    // Generate speech with ElevenLabs
    const audioStream = await elevenlabs.textToSpeech.convert({
      voice_id: process.env.ELEVENLABS_VOICE_ID || "EXAVITQu4vr4xnSDxMaL", // Bella voice
      text: text,
      model_id: "eleven_monolingual_v1",
    });

    // Save audio file
    const audioId = uuidv4();
    const audioPath = path.join(__dirname, 'audio', `${audioId}.mp3`);
    
    // Ensure audio directory exists
    const audioDir = path.join(__dirname, 'audio');
    if (!fs.existsSync(audioDir)) {
      fs.mkdirSync(audioDir, { recursive: true });
    }

    const writeStream = fs.createWriteStream(audioPath);
    audioStream.pipe(writeStream);

    writeStream.on('finish', () => {
      res.json({ 
        audioUrl: `/audio/${audioId}.mp3`,
        audioId: audioId
      });
    });

    writeStream.on('error', (error) => {
      console.error('Audio generation error:', error);
      res.status(500).json({ error: 'Failed to generate audio' });
    });

  } catch (error) {
    console.error('Speech synthesis error:', error);
    res.status(500).json({ error: 'Failed to synthesize speech' });
  }
});

// Speech-to-text endpoint
app.post('/api/transcribe', upload.single('audio'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'Audio file is required' });
    }

    // Transcribe audio with OpenAI Whisper
    const transcription = await openai.audio.transcriptions.create({
      file: fs.createReadStream(req.file.path),
      model: "whisper-1",
    });

    // Clean up uploaded file
    fs.unlinkSync(req.file.path);

    res.json({ text: transcription.text });
  } catch (error) {
    console.error('Transcription error:', error);
    res.status(500).json({ error: 'Failed to transcribe audio' });
  }
});

// Get conversation history
app.get('/api/conversation/:userId', (req, res) => {
  const { userId } = req.params;
  const conversation = conversations.get(userId) || [];
  
  // Filter out system message
  const userConversation = conversation.filter(msg => msg.role !== 'system');
  
  res.json({ conversation: userConversation });
});

// Socket.IO for real-time communication
io.on('connection', (socket) => {
  console.log('User connected:', socket.id);
  
  socket.on('join_conversation', (userId) => {
    socket.join(userId);
    console.log(`User ${socket.id} joined conversation ${userId}`);
  });

  socket.on('new_message', async (data) => {
    try {
      const { message, userId } = data;
      
      // Broadcast message to all clients in the conversation
      io.to(userId).emit('message_received', {
        message,
        sender: 'user',
        timestamp: new Date().toISOString()
      });

      // Generate AI response
      if (!conversations.has(userId)) {
        conversations.set(userId, [
          { role: 'system', content: bellaPersonality }
        ]);
      }
      
      const conversation = conversations.get(userId);
      conversation.push({ role: 'user', content: message });

      const completion = await openai.chat.completions.create({
        model: 'gpt-4',
        messages: conversation,
        max_tokens: 500,
        temperature: 0.8,
      });

      const response = completion.choices[0].message.content;
      conversation.push({ role: 'assistant', content: response });

      // Broadcast AI response
      io.to(userId).emit('message_received', {
        message: response,
        sender: 'bella',
        timestamp: new Date().toISOString()
      });

    } catch (error) {
      console.error('Socket message error:', error);
      socket.emit('error', { message: 'Failed to process message' });
    }
  });

  socket.on('disconnect', () => {
    console.log('User disconnected:', socket.id);
  });
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`🚀 MyBella AI Server running on port ${PORT}`);
  console.log(`💖 Ready to create amazing conversations!`);
});