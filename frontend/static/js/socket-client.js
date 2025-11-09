/**
 * MyBella Socket.IO Client
 * Handles real-time communication for chat and voice chat
 */

class MyBellaSocket {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.currentChatId = null;
        this.currentUserId = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        
        this.init();
    }

    init() {
        // Initialize Socket.IO connection
        this.socket = io({
            transports: ['websocket', 'polling'],
            autoConnect: true,
            reconnection: true,
            reconnectionAttempts: this.maxReconnectAttempts,
            reconnectionDelay: this.reconnectDelay
        });

        this.setupEventListeners();
    }

    setupEventListeners() {
        // Connection events
        this.socket.on('connect', () => {
            console.log('Connected to MyBella server');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.onConnect();
        });

        this.socket.on('disconnect', (reason) => {
            console.log('Disconnected from MyBella server:', reason);
            this.isConnected = false;
            this.onDisconnect(reason);
        });

        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            this.onConnectionError(error);
        });

        this.socket.on('connection_confirmed', (data) => {
            console.log('Connection confirmed:', data);
            this.currentUserId = data.user_id;
        });

        // Chat events
        this.socket.on('chat_joined', (data) => {
            console.log('Joined chat:', data);
            this.currentChatId = data.chat_id;
            this.onChatJoined(data);
        });

        this.socket.on('new_message', (data) => {
            console.log('New message:', data);
            this.onNewMessage(data);
        });

        this.socket.on('user_typing', (data) => {
            this.onUserTyping(data);
        });

    // Voice chat events
        this.socket.on('voice_call_initiated', (data) => {
            console.log('Voice chat initiated:', data);
            this.onVoiceCallInitiated(data);
        });

        this.socket.on('voice_call_started', (data) => {
            console.log('Voice chat started:', data);
            this.onVoiceCallStarted(data);
        });

        this.socket.on('voice_call_ended', (data) => {
            console.log('Voice chat ended:', data);
            this.onVoiceCallEnded(data);
        });

        this.socket.on('voice_call_disconnected', (data) => {
            console.log('Voice chat disconnected:', data);
            this.onVoiceCallDisconnected(data);
        });

        // Subscription events
        this.socket.on('subscription_updated', (data) => {
            console.log('Subscription updated:', data);
            this.onSubscriptionUpdated(data);
        });

        // Error handling
        this.socket.on('error', (data) => {
            console.error('Socket error:', data);
            this.onError(data);
        });
    }

    // Chat methods
    joinChat(chatId, persona = 'Isabella') {
        if (this.isConnected) {
            this.socket.emit('join_chat', {
                chat_id: chatId,
                persona: persona
            });
        }
    }

    leaveChat(chatId) {
        if (this.isConnected && chatId) {
            this.socket.emit('leave_chat', {
                chat_id: chatId
            });
            this.currentChatId = null;
        }
    }

    sendMessage(chatId, message, persona = 'Isabella') {
        if (this.isConnected && chatId && message.trim()) {
            this.socket.emit('send_message', {
                chat_id: chatId,
                message: message.trim(),
                persona: persona
            });
        }
    }

    startTyping(chatId) {
        if (this.isConnected && chatId) {
            this.socket.emit('typing_start', {
                chat_id: chatId
            });
        }
    }

    stopTyping(chatId) {
        if (this.isConnected && chatId) {
            this.socket.emit('typing_stop', {
                chat_id: chatId
            });
        }
    }

    // Voice chat methods
    startVoiceCall(callId, persona) {
        if (this.isConnected) {
            this.socket.emit('voice_call_start', {
                call_id: callId,
                persona: persona
            });
        }
    }

    endVoiceCall(callId) {
        if (this.isConnected) {
            this.socket.emit('voice_call_end', {
                call_id: callId
            });
        }
    }

    // Event handlers (to be overridden)
    onConnect() {
        // Show connection status
        this.updateConnectionStatus(true);
    }

    onDisconnect(reason) {
        // Show disconnection status
        this.updateConnectionStatus(false);
    }

    onConnectionError(error) {
        console.error('Connection failed:', error);
    }

    onChatJoined(data) {
        // Update UI to show chat joined
    }

    onNewMessage(data) {
        // Add message to chat UI
        this.addMessageToChat(data);
    }

    onUserTyping(data) {
        // Show/hide typing indicator
        this.updateTypingIndicator(data);
    }

    onVoiceCallInitiated(data) {
        // Show call initiated status
        this.updateVoiceCallStatus('initiated', data);
    }

    onVoiceCallStarted(data) {
        // Show call active status
        this.updateVoiceCallStatus('active', data);
    }

    onVoiceCallEnded(data) {
        // Show call ended, update minutes
        this.updateVoiceCallStatus('ended', data);
        if (data.minutes_used) {
            this.showCallSummary(data);
        }
    }

    onVoiceCallDisconnected(data) {
        // Handle unexpected disconnection
        this.updateVoiceCallStatus('disconnected', data);
    }

    onSubscriptionUpdated(data) {
        // Update subscription minutes display
        this.updateSubscriptionDisplay(data.minutes_remaining);
    }

    onError(data) {
        // Show error message
        this.showError(data.message);
    }

    // UI Helper methods
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.className = connected ? 'connected' : 'disconnected';
            statusElement.textContent = connected ? 'Connected' : 'Disconnected';
        }
    }

    addMessageToChat(data) {
        const chatContainer = document.getElementById('chat-messages');
        if (chatContainer) {
            const messageElement = document.createElement('div');
            messageElement.className = `message ${data.role}`;
            messageElement.innerHTML = `
                <div class="message-content">
                    <div class="message-text">${this.escapeHtml(data.message)}</div>
                    <div class="message-time">${new Date(data.timestamp).toLocaleTimeString()}</div>
                </div>
            `;
            chatContainer.appendChild(messageElement);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    updateTypingIndicator(data) {
        const typingElement = document.getElementById('typing-indicator');
        if (typingElement) {
            if (data.typing) {
                typingElement.textContent = `${data.user_name} is typing...`;
                typingElement.style.display = 'block';
            } else {
                typingElement.style.display = 'none';
            }
        }
    }

    updateVoiceCallStatus(status, data) {
        const statusElement = document.getElementById('voice-call-status');
        if (statusElement) {
            statusElement.className = `voice-status ${status}`;
            
            switch (status) {
                case 'initiated':
                    statusElement.textContent = `Call with ${data.persona} initiated...`;
                    break;
                case 'active':
                    statusElement.textContent = `Call with ${data.persona} active`;
                    break;
                case 'ended':
                    statusElement.textContent = `Call ended (${data.duration}s)`;
                    break;
                case 'disconnected':
                    statusElement.textContent = 'Call disconnected';
                    break;
            }
        }
    }

    showCallSummary(data) {
        const summaryElement = document.getElementById('call-summary');
        if (summaryElement) {
            summaryElement.innerHTML = `
                <div class="call-summary">
                    <h4>Call Summary</h4>
                    <p>Duration: ${data.duration} seconds</p>
                    <p>Minutes used: ${data.minutes_used}</p>
                    <p>Persona: ${data.persona}</p>
                </div>
            `;
            summaryElement.style.display = 'block';
        }
    }

    updateSubscriptionDisplay(minutesRemaining) {
        const minutesElement = document.getElementById('minutes-remaining');
        if (minutesElement) {
            minutesElement.textContent = Math.floor(minutesRemaining);
        }
    }

    showError(message) {
        // Create or update error display
        let errorElement = document.getElementById('socket-error');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.id = 'socket-error';
            errorElement.className = 'alert alert-danger';
            document.body.appendChild(errorElement);
        }
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 5000);
    }

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Public methods for external use
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }

    reconnect() {
        if (this.socket) {
            this.socket.connect();
        }
    }

    isSocketConnected() {
        return this.isConnected;
    }

    getCurrentChatId() {
        return this.currentChatId;
    }
}

// Global instance
let myBellaSocket = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if user is authenticated
    if (document.body.dataset.userAuthenticated === 'true') {
        myBellaSocket = new MyBellaSocket();
        
        // Make it globally accessible
        window.myBellaSocket = myBellaSocket;
    }
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MyBellaSocket;
}