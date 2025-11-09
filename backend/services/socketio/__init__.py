"""
Socket.IO Service Package
Real-time communication for MyBella
"""

from .socketio_service import (
    socketio,
    init_socketio,
    emit_to_user,
    emit_to_chat,
    emit_ai_response,
    emit_subscription_update,
    get_active_users,
    get_active_calls
)

__all__ = [
    'socketio',
    'init_socketio',
    'emit_to_user',
    'emit_to_chat',
    'emit_ai_response',
    'emit_subscription_update',
    'get_active_users',
    'get_active_calls'
]