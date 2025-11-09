/**
 * Simple Voice Conversation Handler for MyBella
 * Integrated voice conversation in chat (no call system needed)
 */

class VoiceConversation {
    constructor() {
        this.isListening = false;
        this.isSpeaking = false;
        this.recognition = null;
        this.currentPersona = 'Isabella';
        this.currentAudio = null;
        
        this.init();
    }
    
    init() {
        // Check browser support for speech recognition
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn('Speech recognition not supported in this browser');
            this.disableVoiceButton();
            return;
        }
        
        // Setup speech recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';
        this.recognition.maxAlternatives = 1;
        
        // Event handlers
        this.recognition.onstart = () => {
            console.log('Voice recognition started');
            this.updateUI('listening');
        };
        
        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const confidence = event.results[0][0].confidence;
            console.log('Speech recognized:', transcript, 'Confidence:', confidence);
            this.handleSpeech(transcript);
        };
        
        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.handleError(event.error);
            this.stopListening();
        };
        
        this.recognition.onend = () => {
            console.log('Voice recognition ended');
            if (this.isListening) {
                // Restart if still in listening mode
                setTimeout(() => {
                    if (this.isListening) {
                        this.recognition.start();
                    }
                }, 100);
            } else {
                this.updateUI('idle');
            }
        };
        
        // Setup button listeners
        this.setupEventListeners();
        
        // Check voice availability
        this.checkVoiceStatus();

        // Ensure default UI state icon is visible
        this.updateUI('idle');
    }
    
    setupEventListeners() {
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggle();
            });
        }
    }
    
    async checkVoiceStatus() {
        try {
            const response = await fetch('/api/chat/voice/status');
            const data = await response.json();
            
            if (!data.available) {
                console.warn('Voice feature not available - API key missing');
                this.disableVoiceButton();
            } else {
                console.log('Voice feature available');
            }
        } catch (error) {
            console.error('Failed to check voice status:', error);
        }
    }
    
    disableVoiceButton() {
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.disabled = true;
            voiceBtn.style.opacity = '0.5';
            voiceBtn.title = 'Voice not available';
        }
    }
    
    async toggle() {
        if (this.isListening) {
            await this.stopListening();
        } else {
            await this.startListening();
        }
    }
    
    async startListening() {
        try {
            // Request microphone permission
            const hasPermission = await this.checkMicrophonePermission();
            if (!hasPermission) {
                return;
            }
            
            // Get current persona from UI
            this.currentPersona = this.getCurrentPersona();
            
            // Notify server
            await fetch('/api/chat/voice/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    enabled: true,
                    persona: this.currentPersona
                })
            });
            
            // Start recognition
            this.recognition.start();
            this.isListening = true;
            this.updateUI('listening');
            
            console.log('Voice listening started');
            
        } catch (error) {
            console.error('Failed to start listening:', error);
            this.showError('Failed to start voice mode. Please try again.');
        }
    }
    
    async stopListening() {
        try {
            // Stop recognition
            if (this.recognition) {
                this.recognition.stop();
            }
            
            // Stop any playing audio
            if (this.currentAudio) {
                this.currentAudio.pause();
                this.currentAudio = null;
            }
            
            this.isListening = false;
            this.updateUI('idle');
            
            // Notify server
            await fetch('/api/chat/voice/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled: false })
            });
            
            console.log('Voice listening stopped');
            
        } catch (error) {
            console.error('Failed to stop listening:', error);
        }
    }
    
    async checkMicrophonePermission() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            // Stop the stream immediately - we just needed permission
            stream.getTracks().forEach(track => track.stop());
            return true;
        } catch (error) {
            console.error('Microphone permission denied:', error);
            alert('Microphone access denied. Please enable microphone permissions in your browser settings.');
            return false;
        }
    }
    
    getCurrentPersona() {
        const activePersona = document.querySelector('.persona-option.active');
        if (activePersona) {
            return activePersona.dataset.persona || 'Isabella';
        }
        return 'Isabella';
    }
    
    async handleSpeech(text) {
        console.log('Handling speech:', text);
        
        // Temporarily stop listening while processing
        const wasListening = this.isListening;
        if (wasListening) {
            this.recognition.stop();
        }
        
        // Send as regular chat message
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.value = text;
            
            // Trigger form submission
            const chatForm = document.getElementById('chatForm');
            if (chatForm) {
                // Use the existing sendMessage function if available
                if (typeof window.sendMessage === 'function') {
                    window.sendMessage();
                } else {
                    chatForm.dispatchEvent(new Event('submit', { cancelable: true }));
                }
            }
        }
        
        // Wait for AI response, then speak it
        // We'll hook into the chat response to trigger TTS
        setTimeout(() => {
            this.speakLastBotMessage();
            
            // Resume listening if it was active
            if (wasListening && this.isListening) {
                setTimeout(() => {
                    this.recognition.start();
                }, 1000);
            }
        }, 2000);
    }
    
    async speakLastBotMessage() {
        // Get last bot message from chat
        const messages = document.querySelectorAll('.message.bot-message, .bot-message');
        const lastMessage = messages[messages.length - 1];
        
        if (!lastMessage) {
            console.warn('No bot message found to speak');
            return;
        }
        
        // Extract text from message
        const messageText = lastMessage.querySelector('.message-text, .message-bubble p');
        if (!messageText) {
            console.warn('No message text found');
            return;
        }
        
        const text = messageText.textContent.trim();
        if (!text) {
            return;
        }
        
        await this.speakText(text);
    }
    
    async speakText(text) {
        try {
            this.updateUI('speaking');
            
            const response = await fetch('/api/chat/voice/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: text,
                    persona: this.currentPersona
                })
            });
            
            if (response.ok) {
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                
                // Stop any currently playing audio
                if (this.currentAudio) {
                    this.currentAudio.pause();
                }
                
                this.currentAudio = new Audio(audioUrl);
                
                this.currentAudio.onended = () => {
                    URL.revokeObjectURL(audioUrl);
                    this.currentAudio = null;
                    this.isSpeaking = false;
                    
                    if (this.isListening) {
                        this.updateUI('listening');
                    } else {
                        this.updateUI('idle');
                    }
                };
                
                this.currentAudio.onerror = (error) => {
                    console.error('Audio playback error:', error);
                    this.isSpeaking = false;
                    this.updateUI('listening');
                };
                
                this.isSpeaking = true;
                await this.currentAudio.play();
                
            } else {
                // Try graceful fallback to Web Speech API if available
                try {
                    const error = await response.json();
                    console.error('TTS error:', error);
                } catch (e) {
                    console.error('TTS error (non-JSON):', e);
                }
                const fallbackUsed = this.tryBrowserTTSFallback(text);
                if (!fallbackUsed) {
                    this.showError('Voice generation failed');
                }
                this.updateUI('listening');
            }
            
        } catch (error) {
            console.error('TTS generation error:', error);
            const fallbackUsed = this.tryBrowserTTSFallback(text);
            if (!fallbackUsed) {
                this.showError('Voice playback failed');
            }
            this.updateUI('listening');
        }
    }

    tryBrowserTTSFallback(text) {
        try {
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 1.0;
                utterance.pitch = 1.0;
                utterance.lang = 'en-US';
                this.isSpeaking = true;
                this.updateUI('speaking');
                utterance.onend = () => {
                    this.isSpeaking = false;
                    if (this.isListening) {
                        this.updateUI('listening');
                    } else {
                        this.updateUI('idle');
                    }
                };
                window.speechSynthesis.speak(utterance);
                return true;
            }
        } catch (e) {
            console.warn('Browser TTS fallback failed:', e);
        }
        return false;
    }
    
    updateUI(state) {
        const voiceBtn = document.getElementById('voiceBtn');
        if (!voiceBtn) return;
        
        // Remove all state classes
        voiceBtn.classList.remove('voice-idle', 'voice-listening', 'voice-speaking');
        
        switch (state) {
            case 'listening':
                voiceBtn.classList.add('voice-listening');
                voiceBtn.innerHTML = '🎙️';
                voiceBtn.title = 'Listening... (click to stop)';
                break;
                
            case 'speaking':
                voiceBtn.classList.add('voice-speaking');
                voiceBtn.innerHTML = '🔊';
                voiceBtn.title = 'Speaking...';
                break;
                
            case 'idle':
            default:
                voiceBtn.classList.add('voice-idle');
                voiceBtn.innerHTML = '🎤';
                voiceBtn.title = 'Start voice conversation';
                break;
        }
    }
    
    handleError(errorType) {
        let message = 'Voice error occurred';
        
        switch (errorType) {
            case 'no-speech':
                message = 'No speech detected. Please try again.';
                break;
            case 'audio-capture':
                message = 'Microphone not available';
                break;
            case 'not-allowed':
                message = 'Microphone permission denied';
                break;
            case 'network':
                message = 'Network error. Please check your connection.';
                break;
        }
        
        this.showError(message);
    }
    
    showError(message) {
        console.error('Voice error:', message);
        
        // Show error in UI (you can customize this)
        const errorDiv = document.createElement('div');
        errorDiv.className = 'voice-error-toast';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: #ff4444;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.style.opacity = '0';
            errorDiv.style.transition = 'opacity 0.3s';
            setTimeout(() => errorDiv.remove(), 300);
        }, 3000);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing voice conversation...');
    window.voiceConversation = new VoiceConversation();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoiceConversation;
}
