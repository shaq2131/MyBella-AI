"""
Memory routes for MyBella
View conversation history, search messages, and manage preferences
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from backend.services.memory_service import MemoryService
from backend.database.models.memory_models import ChatMessage
from datetime import datetime, timedelta

memory_bp = Blueprint('memory', __name__, url_prefix='/memory')


@memory_bp.route('/history')
@login_required
def history():
    """View conversation history"""
    # Get filter parameters
    persona = request.args.get('persona', 'all')
    days = int(request.args.get('days', 30))
    
    # Get messages
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    query = ChatMessage.query.filter(
        ChatMessage.user_id == current_user.id,
        ChatMessage.timestamp >= cutoff_date
    )
    
    if persona != 'all':
        query = query.filter_by(persona=persona)
    
    messages = query.order_by(ChatMessage.timestamp.desc()).limit(100).all()
    
    # Get conversation stats
    stats = MemoryService.get_conversation_stats(current_user.id)
    
    # Get available personas (from messages)
    from backend.database.models.models import PersonaProfile
    personas = PersonaProfile.query.all()
    
    return render_template(
        'memory/history.html',
        messages=messages,
        stats=stats,
        personas=personas,
        selected_persona=persona,
        selected_days=days
    )


@memory_bp.route('/search')
@login_required
def search():
    """Search conversation history"""
    query = request.args.get('q', '')
    
    if not query:
        return render_template('memory/search.html', results=[], query='')
    
    # Search messages
    results = MemoryService.search_conversations(current_user.id, query, limit=50)
    
    return render_template(
        'memory/search.html',
        results=results,
        query=query
    )


@memory_bp.route('/preferences')
@login_required
def preferences():
    """View learned preferences"""
    # Get all preferences organized by category
    all_prefs = MemoryService.get_user_preferences(current_user.id)
    
    # Organize by category
    prefs_by_category = {}
    for pref in all_prefs:
        category = pref['category']
        if category not in prefs_by_category:
            prefs_by_category[category] = []
        prefs_by_category[category].append(pref)
    
    return render_template(
        'memory/preferences.html',
        preferences=prefs_by_category
    )


@memory_bp.route('/api/context')
@login_required
def api_context():
    """
    Get conversation context for AI (API endpoint)
    This is what YOUR AI integration will call to get context
    """
    persona = request.args.get('persona', 'Isabella')
    include_prefs = request.args.get('include_preferences', 'true').lower() == 'true'
    include_summary = request.args.get('include_summary', 'true').lower() == 'true'
    
    context = MemoryService.build_ai_context(
        current_user.id,
        persona,
        include_preferences=include_prefs,
        include_summary=include_summary
    )
    
    return jsonify({
        'ok': True,
        'context': context,
        'prompt_text': MemoryService.format_context_for_prompt(context)
    })


@memory_bp.route('/api/save-message', methods=['POST'])
@login_required
def api_save_message():
    """Save a message to history (called by chat interface)"""
    data = request.get_json()
    
    message = MemoryService.save_message(
        user_id=current_user.id,
        role=data.get('role'),
        content=data.get('content'),
        persona=data.get('persona'),
        session_id=data.get('session_id'),
        model=data.get('model')
    )
    
    return jsonify({
        'ok': True,
        'message_id': message.id,
        'timestamp': message.timestamp.isoformat()
    })


@memory_bp.route('/api/save-preference', methods=['POST'])
@login_required
def api_save_preference():
    """Save a user preference"""
    data = request.get_json()
    
    preference = MemoryService.save_preference(
        user_id=current_user.id,
        category=data.get('category'),
        key=data.get('key'),
        value=data.get('value'),
        confidence=data.get('confidence', 1.0),
        learned_from=data.get('learned_from', 'manual')
    )
    
    return jsonify({
        'ok': True,
        'preference_id': preference.id
    })


@memory_bp.route('/api/stats')
@login_required
def api_stats():
    """Get conversation statistics"""
    stats = MemoryService.get_conversation_stats(current_user.id)
    
    return jsonify({
        'ok': True,
        'stats': stats
    })


@memory_bp.route('/export')
@login_required
def export():
    """Export conversation history as JSON"""
    # Get all messages
    messages = ChatMessage.query.filter_by(
        user_id=current_user.id
    ).order_by(ChatMessage.timestamp).all()
    
    # Get all preferences
    preferences = MemoryService.get_user_preferences(current_user.id)
    
    export_data = {
        'user_id': current_user.id,
        'export_date': datetime.utcnow().isoformat(),
        'total_messages': len(messages),
        'messages': [msg.to_dict() for msg in messages],
        'preferences': preferences,
        'stats': MemoryService.get_conversation_stats(current_user.id)
    }
    
    return jsonify(export_data)


@memory_bp.route('/api/memories', methods=['GET'])
@login_required
def get_memories():
    """Get all AI memories (conversation history + preferences) for display"""
    try:
        # Get recent messages (last 100)
        messages = ChatMessage.query.filter_by(
            user_id=current_user.id
        ).order_by(ChatMessage.timestamp.desc()).limit(100).all()
        
        # Get preferences
        preferences = MemoryService.get_user_preferences(current_user.id)
        
        # Get stats
        stats = MemoryService.get_conversation_stats(current_user.id)
        
        return jsonify({
            'success': True,
            'memories': {
                'messages': [msg.to_dict() for msg in messages],
                'preferences': preferences,
                'stats': stats
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@memory_bp.route('/api/memories/export', methods=['GET'])
@login_required
def export_memories_json():
    """Export all memories as downloadable JSON file"""
    try:
        # Get ALL messages (no limit for export)
        messages = ChatMessage.query.filter_by(
            user_id=current_user.id
        ).order_by(ChatMessage.timestamp).all()
        
        preferences = MemoryService.get_user_preferences(current_user.id)
        stats = MemoryService.get_conversation_stats(current_user.id)
        
        export_data = {
            'user': {
                'id': current_user.id,
                'name': current_user.name,
                'email': current_user.email
            },
            'export_date': datetime.utcnow().isoformat(),
            'total_messages': len(messages),
            'messages': [msg.to_dict() for msg in messages],
            'preferences': preferences,
            'stats': stats
        }
        
        from flask import Response
        import json
        
        response = Response(
            json.dumps(export_data, indent=2),
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename=mybella_memories_{current_user.id}_{datetime.utcnow().strftime("%Y%m%d")}.json'
            }
        )
        
        return response
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@memory_bp.route('/api/memories/delete', methods=['POST'])
@login_required
def delete_memories():
    """Delete selected memories or all memories"""
    try:
        data = request.get_json()
        delete_all = data.get('delete_all', False)
        message_ids = data.get('message_ids', [])
        
        from backend.database.models.models import db
        from backend.database.models.memory_models import UserPreference
        
        if delete_all:
            # Delete ALL messages and preferences
            ChatMessage.query.filter_by(user_id=current_user.id).delete()
            UserPreference.query.filter_by(user_id=current_user.id).delete()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'All memories deleted successfully'
            })
        
        elif message_ids:
            # Delete specific messages
            ChatMessage.query.filter(
                ChatMessage.id.in_(message_ids),
                ChatMessage.user_id == current_user.id
            ).delete(synchronize_session=False)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Deleted {len(message_ids)} memories'
            })
        
        else:
            return jsonify({
                'success': False,
                'error': 'No deletion criteria provided'
            }), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

