import React, { useState, useEffect, useRef } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Container,
  Paper,
  Typography,
  Box,
  IconButton,
  TextField,
  Fab,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  Mic,
  MicOff,
  Send,
  VolumeUp,
  VolumeOff,
  Favorite,
  SmartToy,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import io from 'socket.io-client';
import axios from 'axios';

// Beautiful pink/purple theme for MyBella
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#ff6b9d',
      light: '#ffb3d1',
      dark: '#c2185b',
    },
    secondary: {
      main: '#9c27b0',
      light: '#e1bee7',
      dark: '#7b1fa2',
    },
    background: {
      default: '#1a1a2e',
      paper: '#16213e',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b3b3b3',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
      background: 'linear-gradient(45deg, #ff6b9d, #9c27b0)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 107, 157, 0.1)',
        },
      },
    },
  },
});

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bella';
  timestamp: Date;
  audioUrl?: string;
}

const API_BASE = 'http://localhost:3001/api';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [socket, setSocket] = useState<any>(null);
  
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const currentAudioRef = useRef<HTMLAudioElement | null>(null);
  
  const userId = 'user_' + Math.random().toString(36).substr(2, 9);

  // Initialize socket connection
  useEffect(() => {
    const newSocket = io('http://localhost:3001');
    setSocket(newSocket);
    
    newSocket.emit('join_conversation', userId);
    
    newSocket.on('message_received', (data: any) => {
      const newMessage: Message = {
        id: Date.now().toString(),
        text: data.message,
        sender: data.sender,
        timestamp: new Date(data.timestamp),
      };
      
      setMessages(prev => [...prev, newMessage]);
      
      // Auto-speak Bella's responses if audio is enabled
      if (data.sender === 'bella' && audioEnabled) {
        speakText(data.message);
      }
    });

    return () => newSocket.close();
  }, [userId, audioEnabled]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Add welcome message
  useEffect(() => {
    const welcomeMessage: Message = {
      id: 'welcome',
      text: "Hi there! I'm Bella, your AI companion. I'm here to chat, listen, and be your friend. How are you feeling today? 💖",
      sender: 'bella',
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
    
    if (audioEnabled) {
      setTimeout(() => speakText(welcomeMessage.text), 1000);
    }
  }, []);

  const sendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // Send via socket for real-time experience
      socket?.emit('new_message', {
        message: text.trim(),
        userId: userId,
      });
    } catch (error) {
      console.error('Error sending message:', error);
      // Fallback to direct API call
      try {
        const response = await axios.post(`${API_BASE}/chat`, {
          message: text.trim(),
          userId: userId,
        });
        
        const bellaMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: response.data.response,
          sender: 'bella',
          timestamp: new Date(),
        };
        
        setMessages(prev => [...prev, bellaMessage]);
        
        if (audioEnabled) {
          speakText(response.data.response);
        }
      } catch (fallbackError) {
        console.error('Fallback error:', fallbackError);
      }
    }
    
    setIsLoading(false);
  };

  const speakText = async (text: string) => {
    if (!audioEnabled) return;
    
    try {
      setIsSpeaking(true);
      
      const response = await axios.post(`${API_BASE}/speak`, {
        text: text,
        userId: userId,
      });
      
      const audio = new Audio(`http://localhost:3001${response.data.audioUrl}`);
      currentAudioRef.current = audio;
      
      audio.onended = () => {
        setIsSpeaking(false);
        currentAudioRef.current = null;
      };
      
      audio.onerror = () => {
        setIsSpeaking(false);
        currentAudioRef.current = null;
      };
      
      await audio.play();
    } catch (error) {
      console.error('Error playing audio:', error);
      setIsSpeaking(false);
    }
  };

  const startListening = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };
      
      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');
        
        try {
          setIsLoading(true);
          const response = await axios.post(`${API_BASE}/transcribe`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });
          
          if (response.data.text) {
            await sendMessage(response.data.text);
          }
        } catch (error) {
          console.error('Transcription error:', error);
        } finally {
          setIsLoading(false);
        }
        
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorderRef.current.start();
      setIsListening(true);
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopListening = () => {
    if (mediaRecorderRef.current && isListening) {
      mediaRecorderRef.current.stop();
      setIsListening(false);
    }
  };

  const toggleAudio = () => {
    setAudioEnabled(!audioEnabled);
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      setIsSpeaking(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="md" sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Paper 
          elevation={3} 
          sx={{ 
            p: 2, 
            mt: 2, 
            background: 'linear-gradient(135deg, rgba(255,107,157,0.1), rgba(156,39,176,0.1))',
            borderRadius: 3,
          }}
        >
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <Avatar sx={{ bgcolor: 'primary.main' }}>
                <Favorite />
              </Avatar>
              <Typography variant="h4">
                MyBella AI
              </Typography>
            </Box>
            <Box>
              <IconButton onClick={toggleAudio} color={audioEnabled ? 'primary' : 'default'}>
                {audioEnabled ? <VolumeUp /> : <VolumeOff />}
              </IconButton>
              {isSpeaking && <Chip label="Speaking..." color="primary" size="small" />}
            </Box>
          </Box>
        </Paper>

        {/* Chat Messages */}
        <Paper 
          elevation={3} 
          sx={{ 
            flex: 1, 
            mt: 2, 
            p: 1, 
            overflow: 'hidden',
            borderRadius: 3,
          }}
        >
          <List sx={{ height: '100%', overflow: 'auto', py: 1 }}>
            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <ListItem 
                    sx={{ 
                      flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
                      alignItems: 'flex-start',
                    }}
                  >
                    <ListItemAvatar>
                      <Avatar 
                        sx={{ 
                          bgcolor: message.sender === 'bella' ? 'primary.main' : 'secondary.main',
                          ml: message.sender === 'user' ? 1 : 0,
                          mr: message.sender === 'bella' ? 1 : 0,
                        }}
                      >
                        {message.sender === 'bella' ? <Favorite /> : <SmartToy />}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Paper
                          elevation={1}
                          sx={{
                            p: 2,
                            bgcolor: message.sender === 'bella' 
                              ? 'rgba(255,107,157,0.1)' 
                              : 'rgba(156,39,176,0.1)',
                            borderRadius: 2,
                            maxWidth: '80%',
                            ml: message.sender === 'user' ? 'auto' : 0,
                            mr: message.sender === 'bella' ? 'auto' : 0,
                          }}
                        >
                          <Typography variant="body1">
                            {message.text}
                          </Typography>
                        </Paper>
                      }
                      secondary={
                        <Typography 
                          variant="caption" 
                          sx={{ 
                            textAlign: message.sender === 'user' ? 'right' : 'left',
                            display: 'block',
                            mt: 0.5,
                          }}
                        >
                          {message.timestamp.toLocaleTimeString()}
                        </Typography>
                      }
                    />
                  </ListItem>
                </motion.div>
              ))}
            </AnimatePresence>
            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <ListItem>
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: 'primary.main' }}>
                      <Favorite />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Bella is thinking...
                        </Typography>
                        <LinearProgress sx={{ mt: 1, borderRadius: 1 }} />
                      </Box>
                    }
                  />
                </ListItem>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </List>
        </Paper>

        {/* Input Area */}
        <Paper 
          elevation={3} 
          sx={{ 
            p: 2, 
            mt: 2, 
            mb: 2,
            borderRadius: 3,
            background: 'linear-gradient(135deg, rgba(255,107,157,0.05), rgba(156,39,176,0.05))',
          }}
        >
          <Box display="flex" alignItems="center" gap={2}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type your message to Bella..."
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage(inputText);
                }
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                },
              }}
            />
            <IconButton
              color="primary"
              onClick={() => sendMessage(inputText)}
              disabled={!inputText.trim() || isLoading}
            >
              <Send />
            </IconButton>
            <Fab
              color={isListening ? 'secondary' : 'primary'}
              size="medium"
              onClick={isListening ? stopListening : startListening}
              disabled={isLoading}
              sx={{
                background: isListening 
                  ? 'linear-gradient(45deg, #f44336, #e91e63)'
                  : 'linear-gradient(45deg, #ff6b9d, #9c27b0)',
              }}
            >
              {isListening ? <MicOff /> : <Mic />}
            </Fab>
          </Box>
        </Paper>
      </Container>
    </ThemeProvider>
  );
}

export default App;