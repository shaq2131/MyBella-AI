"""
Socket.IO Service for MyBella
Real-time communication for chat and voice calling
"""

from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask_login import current_user
from flask import request
import logging
from typing import Dict, Any
from datetime import datetime

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*", logger=True, engineio_logger=True)

# Store active users and their rooms
active_users = {}
active_calls = {}

def init_socketio(app):
    """Initialize SocketIO with Flask app"""
    socketio.init_app(app, 
                     cors_allowed_origins="*",
                     async_mode='threading',  # Threading mode for Python 3.13 compatibility
                     ping_timeout=60,
                     ping_interval=25)
    return socketio

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    if current_user.is_authenticated:
        user_id = str(current_user.id)
        active_users[user_id] = {
            'sid': request.sid,
            'connected_at': datetime.utcnow(),
            'user_info': {
                'id': current_user.id,
                'name': current_user.name,
                'email': current_user.email
            }
        }
        
        # Join user to their personal room
        join_room(f"user_{user_id}")
        
        logging.info(f"User {current_user.name} connected with SID: {request.sid}")
        
        emit('connection_confirmed', {
            'status': 'connected',
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        })
    else:
        logging.warning("Unauthorized connection attempt")
        disconnect()

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    if current_user.is_authenticated:
        user_id = str(current_user.id)
        
        # Remove from active users
        if user_id in active_users:
            del active_users[user_id]
        
        # Handle any active voice calls
        if user_id in active_calls:
            handle_call_disconnect(user_id)
        
        logging.info(f"User {current_user.name} disconnected")

@socketio.on('join_chat')
def handle_join_chat(data):
    """Join a chat room for real-time messaging"""
    if not current_user.is_authenticated:
        emit('error', {'message': 'Authentication required'})
        return
    
    chat_id = data.get('chat_id')
    persona = data.get('persona', 'Isabella')
    
    if not chat_id:
        emit('error', {'message': 'Chat ID required'})
        return
    
    room = f"chat_{chat_id}"
    join_room(room)
    
    emit('chat_joined', {
        'chat_id': chat_id,
        'persona': persona,
        'room': room,
        'timestamp': datetime.utcnow().isoformat()
    })
    
    logging.info(f"User {current_user.name} joined chat {chat_id}")

@socketio.on('leave_chat')
def handle_leave_chat(data):
    """Leave a chat room"""
    if not current_user.is_authenticated:
        return
    
    chat_id = data.get('chat_id')
    if chat_id:
        room = f"chat_{chat_id}"
        leave_room(room)
        
        emit('chat_left', {
            'chat_id': chat_id,
            'timestamp': datetime.utcnow().isoformat()
        })

@socketio.on('send_message')
def handle_send_message(data):
    """Handle real-time message sending"""
    if not current_user.is_authenticated:
        emit('error', {'message': 'Authentication required'})
        return
    
    chat_id = data.get('chat_id')
    message = data.get('message', '').strip()
    persona = data.get('persona', 'Isabella')
    
    if not chat_id or not message:
        emit('error', {'message': 'Chat ID and message required'})
        return
    
    # Emit message to chat room
    room = f"chat_{chat_id}"
    
    message_data = {
        'chat_id': chat_id,
        'user_id': current_user.id,
        'user_name': current_user.name,
        'message': message,
        'persona': persona,
        'role': 'user',
        'timestamp': datetime.utcnow().isoformat()
    }
    
    socketio.emit('new_message', message_data, room=room)
    
    logging.info(f"Message sent in chat {chat_id} by {current_user.name}")

@socketio.on('typing_start')
def handle_typing_start(data):
    """Handle typing indicator start"""
    if not current_user.is_authenticated:
        return
    
    chat_id = data.get('chat_id')
    if chat_id:
        room = f"chat_{chat_id}"
        socketio.emit('user_typing', {
            'user_id': current_user.id,
            'user_name': current_user.name,
            'typing': True,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room, include_self=False)

@socketio.on('typing_stop')
def handle_typing_stop(data):
    """Handle typing indicator stop"""
    if not current_user.is_authenticated:
        return
    
    chat_id = data.get('chat_id')
    if chat_id:
        room = f"chat_{chat_id}"
        socketio.emit('user_typing', {
            'user_id': current_user.id,
            'user_name': current_user.name,
            'typing': False,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room, include_self=False)

# Voice Calling Real-time Events

@socketio.on('voice_call_start')
def handle_voice_call_start(data):
    """Handle voice call initiation"""
    if not current_user.is_authenticated:
        emit('error', {'message': 'Authentication required'})
        return
    
    call_id = data.get('call_id')
    persona = data.get('persona')
    
    if not call_id or not persona:
        emit('error', {'message': 'Call ID and persona required'})
        return
    
    user_id = str(current_user.id)
    
    # Store active call
    active_calls[user_id] = {
        'call_id': call_id,
        'persona': persona,
        'started_at': datetime.utcnow(),
        'status': 'active'
    }
    
    # Join call room
    call_room = f"call_{call_id}"
    join_room(call_room)
    
    # Emit to user's personal room
    socketio.emit('voice_call_started', {
        'call_id': call_id,
        'persona': persona,
        'status': 'active',
        'timestamp': datetime.utcnow().isoformat()
    }, room=f"user_{user_id}")
    
    logging.info(f"Voice call {call_id} started by user {current_user.name}")

@socketio.on('voice_call_end')
def handle_voice_call_end(data):
    """Handle voice call termination"""
    if not current_user.is_authenticated:
        return
    
    user_id = str(current_user.id)
    call_id = data.get('call_id')
    
    if user_id in active_calls:
        call_info = active_calls[user_id]
        
        # Leave call room
        call_room = f"call_{call_info['call_id']}"
        leave_room(call_room)
        
        # Remove from active calls
        del active_calls[user_id]
        
        # Emit to user's personal room
        socketio.emit('voice_call_ended', {
            'call_id': call_info['call_id'],
            'persona': call_info['persona'],
            'duration': (datetime.utcnow() - call_info['started_at']).total_seconds(),
            'timestamp': datetime.utcnow().isoformat()
        }, room=f"user_{user_id}")
        
        logging.info(f"Voice call {call_info['call_id']} ended by user {current_user.name}")

@socketio.on('subscription_update')
def handle_subscription_update(data):
    """Handle subscription minutes update"""
    if not current_user.is_authenticated:
        return
    
    user_id = str(current_user.id)
    minutes_remaining = data.get('minutes_remaining', 0)
    
    # Emit to user's personal room
    socketio.emit('subscription_updated', {
        'minutes_remaining': minutes_remaining,
        'timestamp': datetime.utcnow().isoformat()
    }, room=f"user_{user_id}")

def handle_call_disconnect(user_id: str):
    """Handle unexpected disconnection during voice call"""
    if user_id in active_calls:
        call_info = active_calls[user_id]
        
        # Notify about unexpected disconnection
        socketio.emit('voice_call_disconnected', {
            'call_id': call_info['call_id'],
            'persona': call_info['persona'],
            'reason': 'connection_lost',
            'timestamp': datetime.utcnow().isoformat()
        }, room=f"user_{user_id}")
        
        # Clean up
        del active_calls[user_id]
        
        logging.warning(f"Voice call {call_info['call_id']} disconnected unexpectedly for user {user_id}")

# Enhanced Voice Call Socket Events

@socketio.on('voice_speech_input')
def handle_voice_speech_input(data):
    """Handle voice speech input during call"""
    if not current_user.is_authenticated:
        emit('error', {'message': 'Authentication required'})
        return
    
    call_id = data.get('call_id')
    speech_text = data.get('speech', '').strip()
    mode = data.get('mode', 'Companion')
    
    if not call_id or not speech_text:
        emit('error', {'message': 'Call ID and speech text required'})
        return
    
    try:
        from backend.services.voice import process_voice_input
        result = process_voice_input(call_id, speech_text, mode)
        
        if result.get('success'):
            emit('voice_speech_processed', {
                'call_id': call_id,
                'ai_response': result.get('ai_response'),
                'tts_audio': result.get('tts_audio'),
                'conversation_length': result.get('conversation_length')
            })
        else:
            emit('error', {'message': result.get('error', 'Failed to process speech')})
            
    except Exception as e:
        logging.error(f"Error processing voice speech: {str(e)}")
        emit('error', {'message': 'Error processing speech input'})

@socketio.on('voice_session_heartbeat')
def handle_voice_session_heartbeat(data):
    """Handle voice session heartbeat to keep session alive"""
    if not current_user.is_authenticated:
        return
    
    call_id = data.get('call_id')
    if call_id:
        user_id = str(current_user.id)
        if user_id in active_calls:
            active_calls[user_id]['last_heartbeat'] = datetime.utcnow()
            
            emit('voice_session_heartbeat_ack', {
                'call_id': call_id,
                'timestamp': datetime.utcnow().isoformat()
            })

# Utility functions for emitting to specific users

def emit_to_user(user_id: int, event: str, data: Dict[str, Any]):
    """Emit event to specific user"""
    socketio.emit(event, data, room=f"user_{user_id}")

def emit_to_chat(chat_id: int, event: str, data: Dict[str, Any]):
    """Emit event to specific chat"""
    socketio.emit(event, data, room=f"chat_{chat_id}")

def emit_ai_response(chat_id: int, persona: str, message: str):
    """Emit AI response to chat"""
    emit_to_chat(chat_id, 'new_message', {
        'chat_id': chat_id,
        'message': message,
        'persona': persona,
        'role': 'assistant',
        'timestamp': datetime.utcnow().isoformat()
    })

def emit_subscription_update(user_id: int, minutes_remaining: float):
    """Emit subscription update to user"""
    emit_to_user(user_id, 'subscription_updated', {
        'minutes_remaining': minutes_remaining,
        'timestamp': datetime.utcnow().isoformat()
    })

def emit_voice_message(user_id: int, call_id: int, persona: str, message: str, audio_b64: str = None):
    """Emit voice message with TTS audio"""
    emit_to_user(user_id, 'voice_call_message', {
        'call_id': call_id,
        'persona': persona,
        'message': message,
        'audio_b64': audio_b64,
        'timestamp': datetime.utcnow().isoformat()
    })

def get_active_users():
    """Get list of currently active users"""
    return active_users

def get_active_calls():
    """Get list of currently active voice calls"""
    return active_calls