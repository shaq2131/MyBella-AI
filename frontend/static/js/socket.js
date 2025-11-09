/**
 * Socket.IO Real-time Communication Handler
 * Manages WebSocket connections for chat, voice chat, and real-time updates
 */

class SocketManager {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.init();
    }

    init() {
        if (typeof io !== 'undefined') {
            this.connect();
            this.setupEventListeners();
        } else {
            console.warn('Socket.IO not loaded');
        }
    }

    connect() {
        try {
            this.socket = io({
                transports: ['websocket', 'polling'],
                upgrade: true,
                rememberUpgrade: true
            });

            this.socket.on('connect', () => {
                console.log('🔌 Connected to MyBella server');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.onConnect();
            });

            this.socket.on('disconnect', (reason) => {
                console.log('🔌 Disconnected from MyBella server:', reason);
                this.isConnected = false;
                this.onDisconnect(reason);
            });

            this.socket.on('connect_error', (error) => {
                console.error('🔌 Connection error:', error);
                this.handleReconnection();
            });

        } catch (error) {
            console.error('Failed to initialize socket connection:', error);
        }
    }

    setupEventListeners() {
        if (!this.socket) return;

        // Chat events
        this.socket.on('message_received', (data) => {
            this.handleMessageReceived(data);
        });

        this.socket.on('typing_start', (data) => {
            this.handleTypingStart(data);
        });

        this.socket.on('typing_stop', (data) => {
            this.handleTypingStop(data);
        });

    // Voice chat events
        this.socket.on('voice_call_incoming', (data) => {
            this.handleIncomingVoiceCall(data);
        });

        this.socket.on('voice_call_started', (data) => {
            this.handleVoiceCallStarted(data);
        });

        this.socket.on('voice_call_ended', (data) => {
            this.handleVoiceCallEnded(data);
        });

        // Subscription updates
        this.socket.on('minutes_updated', (data) => {
            this.handleMinutesUpdate(data);
        });

        // System notifications
        this.socket.on('notification', (data) => {
            this.handleNotification(data);
        });

        // Persona status updates
        this.socket.on('persona_status_update', (data) => {
            this.handlePersonaStatusUpdate(data);
        });
    }

    onConnect() {
        // Join user's personal room
        if (typeof currentUserId !== 'undefined') {
            this.socket.emit('join_user_room', { user_id: currentUserId });
        }

        // Show connection status
        this.updateConnectionStatus(true);
        
        // Notify user if they were disconnected
        if (this.reconnectAttempts > 0) {
            myBella.showAlert('Reconnected to MyBella!', 'success', 3000);
        }
    }

    onDisconnect(reason) {
        this.updateConnectionStatus(false);
        
        // Auto-reconnect for certain disconnect reasons
        if (reason === 'io server disconnect') {
            // Server initiated disconnect, don't auto-reconnect
            myBella.showAlert('Connection lost. Please refresh the page.', 'error');
        } else {
            // Client disconnect, attempt to reconnect
            this.handleReconnection();
        }
    }

    handleReconnection() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            
            setTimeout(() => {
                console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                this.socket.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            myBella.showAlert('Unable to connect to MyBella. Please refresh the page.', 'error');
        }
    }

    updateConnectionStatus(isConnected) {
        const statusElements = document.querySelectorAll('.connection-status');
        statusElements.forEach(element => {
            element.className = `connection-status ${isConnected ? 'connected' : 'disconnected'}`;
            element.textContent = isConnected ? 'Connected' : 'Disconnected';
        });
    }

    // Chat event handlers
    handleMessageReceived(data) {
        console.log('📨 Message received:', data);
        
        // Update chat interface if on chat page
        if (typeof addMessageToChat === 'function') {
            addMessageToChat(data.message, 'ai', data.persona_name);
        }

        // Show notification if not on chat page or window not focused
        if (!document.hasFocus() || !window.location.pathname.includes('/chat')) {
            this.showDesktopNotification(
                `New message from ${data.persona_name}`,
                data.message.substring(0, 100) + (data.message.length > 100 ? '...' : '')
            );
        }

        // Update unread message count
        this.updateUnreadCount(data.persona_id, 1);
    }

    handleTypingStart(data) {
        console.log('⌨️ Typing started:', data);
        if (typeof showTypingIndicator === 'function') {
            showTypingIndicator(data.persona_name);
        }
    }

    handleTypingStop(data) {
        console.log('⌨️ Typing stopped:', data);
        if (typeof hideTypingIndicator === 'function') {
            hideTypingIndicator();
        }
    }

    // Voice chat event handlers
    handleIncomingVoiceCall(data) {
    console.log('🎙️ Incoming voice chat:', data);
        
        if (typeof showIncomingCallModal === 'function') {
            showIncomingCallModal(data);
        } else {
            // Fallback notification
            myBella.showAlert(`Incoming call from ${data.persona_name}`, 'warning');
        }
    }

    handleVoiceCallStarted(data) {
    console.log('🎙️ Voice chat started:', data);
        
        if (typeof onVoiceCallStarted === 'function') {
            onVoiceCallStarted(data);
        }
    }

    handleVoiceCallEnded(data) {
    console.log('🎙️ Voice chat ended:', data);
        
        if (typeof onVoiceCallEnded === 'function') {
            onVoiceCallEnded(data);
        }
        
        myBella.showAlert(`Call ended. Duration: ${this.formatDuration(data.duration)}`, 'success');
    }

    // Subscription event handlers
    handleMinutesUpdate(data) {
        console.log('⏱️ Minutes updated:', data);
        
        // Update minutes display
        const minutesElements = document.querySelectorAll('.minutes-remaining');
        minutesElements.forEach(element => {
            element.textContent = data.minutes_remaining;
        });

        // Show warning if low on minutes
        if (data.minutes_remaining <= 10 && data.minutes_remaining > 0) {
            myBella.showAlert(
                `Warning: Only ${data.minutes_remaining} minutes remaining for voice chat.`,
                'warning'
            );
        } else if (data.minutes_remaining <= 0) {
            myBella.showAlert('No voice chat minutes remaining. Upgrade your plan to continue.', 'error');
        }
    }

    // System notification handler
    handleNotification(data) {
        console.log('🔔 Notification:', data);
        
        myBella.showAlert(data.message, data.type || 'info', data.duration || 5000);
        
        // Show desktop notification if permitted
        if (data.desktop_notification) {
            this.showDesktopNotification(data.title || 'MyBella', data.message);
        }
    }

    // Persona status update handler
    handlePersonaStatusUpdate(data) {
        console.log('🎭 Persona status update:', data);
        
        // Update persona status indicators
        const statusElements = document.querySelectorAll(`.persona-status[data-persona-id="${data.persona_id}"]`);
        statusElements.forEach(element => {
            element.className = `persona-status status-${data.status}`;
            element.textContent = data.status_text;
        });
    }

    // Utility methods
    showDesktopNotification(title, body, icon = '/static/img/icon-192.png') {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: body,
                icon: icon,
                badge: icon,
                tag: 'mybella-notification'
            });
        }
    }

    updateUnreadCount(personaId, increment = 1) {
        const countElements = document.querySelectorAll(`.unread-count[data-persona-id="${personaId}"]`);
        countElements.forEach(element => {
            const currentCount = parseInt(element.textContent) || 0;
            const newCount = currentCount + increment;
            element.textContent = newCount;
            element.style.display = newCount > 0 ? 'block' : 'none';
        });
    }

    formatDuration(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    // Public methods for sending events
    sendMessage(message, personaId) {
        if (this.isConnected) {
            this.socket.emit('send_message', {
                message: message,
                persona_id: personaId,
                timestamp: new Date().toISOString()
            });
        }
    }

    startTyping(personaId) {
        if (this.isConnected) {
            this.socket.emit('start_typing', { persona_id: personaId });
        }
    }

    stopTyping(personaId) {
        if (this.isConnected) {
            this.socket.emit('stop_typing', { persona_id: personaId });
        }
    }

    joinChatRoom(personaId) {
        if (this.isConnected) {
            this.socket.emit('join_chat', { persona_id: personaId });
        }
    }

    leaveChatRoom(personaId) {
        if (this.isConnected) {
            this.socket.emit('leave_chat', { persona_id: personaId });
        }
    }

    startVoiceCall(personaId) {
        if (this.isConnected) {
            this.socket.emit('start_voice_call', { persona_id: personaId });
        }
    }

    endVoiceCall(callId) {
        if (this.isConnected) {
            this.socket.emit('end_voice_call', { call_id: callId });
        }
    }

    // Disconnect method
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// Initialize socket manager when script loads
let socketManager;

document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if user is authenticated
    if (typeof currentUserId !== 'undefined' && currentUserId) {
        socketManager = new SocketManager();
        
        // Make it globally available
        window.socket = socketManager.socket;
        window.socketManager = socketManager;
    }
});

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (socketManager) {
        if (document.hidden) {
            console.log('📱 Page hidden - maintaining connection');
        } else {
            console.log('📱 Page visible - ensuring connection');
            if (!socketManager.isConnected) {
                socketManager.connect();
            }
        }
    }
});

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    if (socketManager) {
        socketManager.disconnect();
    }
});