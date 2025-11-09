"""
API routes for MyBella
Handles chat, TTS, voice upload endpoints, and real-time communication
"""

from flask import Blueprint, request, jsonify, send_file, session, current_app
from flask_login import login_required, current_user
from backend.database.models.models import db, Message, PersonaProfile
from backend.database.utils.utils import get_user_id, get_persona, get_mode, get_tts_enabled, safe_filename, allowed_audio_file
from backend.services.chat.chat_service import get_ai_response
from backend.services.firebase.firebase_service import store_message_firestore
from backend.services.chat.pinecone_service import pinecone_upsert
from backend.services.elevenlabs.tts_service import generate_speech, upload_voice
from backend.services.socketio import emit_ai_response, emit_subscription_update
from backend.services.voice.voice_conversation_service import VoiceConversationService, generate_voice
from backend.services.crisis_detection import detect_crisis, get_crisis_response, log_crisis_event, should_block_ai_response
from backend.services.achievements_service import AchievementsService
from backend.funcs.users import update_user_profile_picture, get_user_profile_picture_url, UserCRUDError
from backend.funcs.personas.persona_crud import (
    update_persona_profile_picture, get_persona_profile_picture_url, 
    PersonaCRUDError, get_persona_with_picture_info
)
import io

api_bp = Blueprint('api', __name__)

@api_bp.route('/chat', methods=['POST'])
@login_required
def api_chat():
    """Handle chat messages with real-time support and crisis detection"""
    data = request.get_json(force=True)
    user_text = (data.get('text') or '').strip()
    persona = (data.get('persona') or get_persona()).capitalize()
    mode = data.get('mode') or get_mode()
    chat_id = data.get('chat_id')  # For real-time room support
    use_voice = data.get('use_voice', False)  # NEW: Voice mode flag from frontend
    
    if not user_text:
        return jsonify({"error": "Empty message"}), 400

    user_id = get_user_id()
    
    # Get persona_id for memory isolation
    persona_profile = PersonaProfile.query.filter_by(name=persona).first()
    persona_id = persona_profile.id if persona_profile else None
    
    # Crisis detection - check user message for high-risk indicators
    is_crisis, severity, matched_keywords = detect_crisis(user_text)
    
    if is_crisis:
        # Log crisis event for admin monitoring
        log_crisis_event(user_id, user_text, severity, matched_keywords)
        
        # Get crisis-appropriate response
        crisis_response_data = get_crisis_response(severity)
        
        # For high severity, prioritize crisis resources over AI response
        if should_block_ai_response(severity):
            bot_text = crisis_response_data['message']
        else:
            # Get AI response but prepend crisis resources
            bot_text = crisis_response_data['message'] + "\n\n---\n\n"
            ai_response = get_ai_response(user_text, persona, mode, user_id, persona_id=persona_id)
            bot_text += ai_response
    else:
        # Normal AI response flow (now with persona_id for memory isolation)
        bot_text = get_ai_response(user_text, persona, mode, user_id, persona_id=persona_id)
    
    # Store user message in Firestore
    store_message_firestore(user_id, persona, "user", user_text)

    # Save conversation to database WITH persona_id for memory isolation
    try:
        from backend.database.models.memory_models import ChatMessage
        
        # Save to memory_models.ChatMessage for per-persona history
        user_msg = ChatMessage(
            user_id=current_user.id,
            role="user",
            content=user_text,
            persona=persona,
            persona_id=persona_id  # NEW: Persona-specific memory
        )
        bot_msg = ChatMessage(
            user_id=current_user.id,
            role="assistant",
            content=bot_text,
            persona=persona,
            persona_id=persona_id  # NEW: Persona-specific memory
        )
        db.session.add(user_msg)
        db.session.add(bot_msg)
        
        # Also save to legacy Message table for backward compatibility
        db.session.add(Message(
            user_id=current_user.id,
            role="user",
            content=user_text,
            persona=persona
        ))
        db.session.add(Message(
            user_id=current_user.id,
            role="bot",
            content=bot_text,
            persona=persona
        ))
        db.session.commit()
        
        # 🏆 Check for conversation achievements and update streak
        newly_unlocked = AchievementsService.check_conversation_achievements(current_user.id)
        streak, was_updated, streak_achievements = AchievementsService.record_checkin(current_user.id)
        
    except Exception:
        db.session.rollback()
        newly_unlocked = []
        streak_achievements = []

    # Store in vector database for memory
    pinecone_upsert(user_id, persona, user_text)
    pinecone_upsert(user_id, persona, bot_text)

    # Emit real-time AI response if chat_id provided
    if chat_id:
        try:
            emit_ai_response(chat_id, persona, bot_text)
        except Exception as e:
            # Continue if real-time emission fails
            pass

    # 🎙️ VOICE CHAT - Generate voice response ONLY if user is in voice mode
    voice_response = {'audio_url': None, 'voice_used': False, 'minutes_used': 0.0, 'remaining_minutes': 0.0}
    
    if use_voice:
        # User is in voice mode - generate voice and deduct minutes
        from backend.services.voice_chat_service import VoiceChatService
        voice_response = VoiceChatService.generate_voice_response(
            text=bot_text,
            persona=persona,
            user_id=user_id
        )
    else:
        # Chat mode - skip voice generation entirely (no API costs)
        from backend.services.voice_chat_service import VoiceChatService
        status = VoiceChatService.get_user_voice_status(user_id)
        voice_response['remaining_minutes'] = status.get('remaining_minutes', 0.0)
    
    # Include crisis flag in response for frontend handling
    response_data = {
        "text": bot_text,
        "audio_url": voice_response.get('audio_url'),
        "voice_used": voice_response.get('voice_used', False),
        "voice_minutes_used": voice_response.get('minutes_used', 0.0),
        "voice_minutes_remaining": voice_response.get('remaining_minutes', 0.0)
    }
    
    # 💙 MOOD CONTEXT - Include mood awareness info for frontend
    from backend.services.mood_service import MoodService
    mood_context = MoodService.get_mood_context(user_id)
    
    if mood_context['has_recent_mood']:
        response_data["mood_aware"] = True
        response_data["mood_level"] = mood_context['mood_level']
        response_data["days_since_checkin"] = mood_context['days_since_checkin']
    
    # Suggest mood check-in if needed
    if MoodService.should_suggest_mood_checkin(user_id):
        response_data["suggest_mood_checkin"] = True
        response_data["mood_checkin_prompt"] = MoodService.get_mood_checkin_prompt(persona)
    
    if is_crisis:
        response_data["crisis_detected"] = True
        response_data["severity"] = severity
    
    # Add fallback reason if voice wasn't used
    if use_voice and not voice_response.get('voice_used') and voice_response.get('fallback_reason'):
        response_data["voice_fallback_reason"] = voice_response.get('fallback_reason')
    
    # 🏆 Include newly unlocked achievements in response
    all_new_achievements = newly_unlocked + streak_achievements
    if all_new_achievements:
        response_data["achievements"] = [achievement.to_dict() for achievement in all_new_achievements]
        response_data["crisis_resources_url"] = "/crisis/support"

    return jsonify(response_data)

@api_bp.route('/tts', methods=['POST'])
@login_required
def api_tts():
    """Generate text-to-speech audio"""
    data = request.get_json(force=True)
    text = (data.get('text') or '').strip()
    persona = (data.get('persona') or get_persona()).capitalize()
    voice_id = data.get('voice_id')

    # Check if TTS is enabled for user
    if not get_tts_enabled():
        return jsonify({
            "audio_b64": None,
            "note": "(demo) TTS disabled in Settings."
        })

    if not text:
        return jsonify({"error": "Empty text"}), 400

    user_id = get_user_id()
    result = generate_speech(text, persona, user_id, voice_id)
    
    return jsonify(result)

@api_bp.route('/voice-upload', methods=['POST'])
@login_required
def api_voice_upload():
    """Upload custom voice for persona"""
    persona = (request.form.get('persona') or get_persona()).capitalize()
    voice_name = (request.form.get('voice_name') or persona).strip()[:60]
    file = request.files.get('file')
    
    if not file or not getattr(file, 'filename', None):
        return jsonify({"ok": False, "error": "No file uploaded"}), 400

    filename = safe_filename(file.filename)
    if not allowed_audio_file(filename):
        return jsonify({
            "ok": False,
            "error": "Unsupported file type. Allowed: .mp3, .wav, .m4a"
        }), 400

    user_id = get_user_id()
    result = upload_voice(file, voice_name, persona, user_id)
    
    return jsonify(result)

@api_bp.route('/profile-picture', methods=['POST'])
@login_required
def api_profile_picture_upload():
    """Upload user profile picture"""
    file = request.files.get('file')
    
    if not file or not getattr(file, 'filename', None):
        return jsonify({"ok": False, "error": "No file uploaded"}), 400

    try:
        file_path = update_user_profile_picture(current_user.id, file)
        if file_path:
            return jsonify({
                "ok": True,
                "message": "Profile picture updated successfully",
                "file_path": file_path,
                "url": f"/uploads/{file_path}"
            })
        else:
            return jsonify({"ok": False, "error": "Failed to update profile picture"}), 500
            
    except UserCRUDError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": "An unexpected error occurred"}), 500

@api_bp.route('/persona-picture', methods=['POST'])
@login_required
def api_persona_picture_upload():
    """Upload persona profile picture (admin only for now)"""
    # For now, allow any authenticated user to upload persona pictures
    # In production, you might want to restrict this to admins
    
    persona = request.form.get('persona', '').strip()
    file = request.files.get('file')
    
    if not persona:
        return jsonify({"ok": False, "error": "Persona name required"}), 400
    
    if not file or not getattr(file, 'filename', None):
        return jsonify({"ok": False, "error": "No file uploaded"}), 400

    try:
        file_path = update_persona_profile_picture(persona, file)
        if file_path:
            return jsonify({
                "ok": True,
                "message": f"Profile picture updated for {persona}",
                "persona": persona,
                "file_path": file_path,
                "url": f"/uploads/{file_path}"
            })
        else:
            return jsonify({"ok": False, "error": "Failed to update persona picture"}), 500
            
    except PersonaCRUDError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": "An unexpected error occurred"}), 500

@api_bp.route('/chat-context', methods=['GET'])
@login_required
def api_chat_context():
    """Get chat context including user and persona profile pictures"""
    persona = request.args.get('persona', get_persona())
    
    try:
        # Get user profile picture
        user_pic_url = get_user_profile_picture_url(current_user.id)
        
        # Get persona information with picture
        persona_info = get_persona_with_picture_info(persona)
        
        return jsonify({
            "success": True,
            "user": {
                "id": current_user.id,
                "name": current_user.name,
                "profile_picture_url": user_pic_url
            },
            "persona": persona_info
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to get chat context"
        }), 500


# =============================================================================
# Integrated Voice Conversation Routes
# =============================================================================

@api_bp.route('/chat/voice/toggle', methods=['POST'])
@login_required
def toggle_voice_mode():
    """
    Toggle voice mode on/off in current chat
    Simple state toggle - no complex call management needed
    """
    try:
        data = request.get_json()
        voice_enabled = data.get('enabled', False)
        persona = data.get('persona', get_persona())
        
        # Store in session (lightweight, no database needed)
        from flask import session
        session['voice_mode'] = voice_enabled
        session['voice_persona'] = persona
        
        current_app.logger.info(f'User {current_user.id} toggled voice mode: {voice_enabled} for {persona}')
        
        return jsonify({
            'success': True,
            'voice_mode': voice_enabled,
            'persona': persona,
            'message': f'Voice mode {"activated" if voice_enabled else "deactivated"}'
        })
        
    except Exception as e:
        current_app.logger.error(f'Voice toggle error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/chat/voice/tts', methods=['POST'])
@login_required
def generate_voice_tts():
    """
    Generate TTS audio for AI response
    Returns audio stream directly - no storage
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        persona = data.get('persona', get_persona())
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Check if API key is configured
        if not VoiceConversationService.validate_api_key():
            return jsonify({
                'error': 'Voice feature not configured',
                'message': 'ElevenLabs API key required'
            }), 503
        
        # Generate voice audio
        audio_data = VoiceConversationService.generate_voice_response(text, persona)
        
        if audio_data:
            # Return audio stream (MP3)
            return send_file(
                io.BytesIO(audio_data),
                mimetype='audio/mpeg',
                as_attachment=False,
                download_name=f'{persona}_response.mp3'
            )
        else:
            return jsonify({'error': 'TTS generation failed'}), 500
            
    except Exception as e:
        current_app.logger.error(f'TTS generation error: {e}')
        return jsonify({'error': str(e)}), 500


@api_bp.route('/chat/voice/status', methods=['GET'])
@login_required
def voice_status():
    """
    Get voice chat minutes status with auto-fallback info
    """
    try:
        from backend.services.voice_chat_service import VoiceChatService
        
        # Get voice minutes status
        status = VoiceChatService.get_user_voice_status(get_user_id())
        
        # Include availability based on TTS provider configuration for frontend compatibility
        status['available'] = VoiceConversationService.validate_api_key()
        
        # Also include available personas
        status['personas'] = list(VoiceConversationService.get_available_personas().keys())
        
        return jsonify(status)
        
    except Exception as e:
        current_app.logger.error(f'Voice status error: {e}')
        return jsonify({'error': str(e)}), 500


@api_bp.route('/chat/voice/personas', methods=['GET'])
@login_required
def get_voice_personas():
    """
    Get list of available personas with voice capability
    """
    try:
        personas = VoiceConversationService.get_available_personas()
        
        return jsonify({
            'success': True,
            'personas': [
                {
                    'name': name,
                    'voice_id': voice_id,
                    'available': True
                }
                for name, voice_id in personas.items()
            ]
        })
        
    except Exception as e:
        current_app.logger.error(f'Get personas error: {e}')
        return jsonify({'error': str(e)}), 500