"""
Main view routes for MyBella
Handles home, app, settings, and other public pages
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    current_app,
)
from flask_login import login_required, current_user
from backend.database.models.models import db, UserSettings
from backend.database.utils.utils import get_persona, get_mode
from backend.services.firebase.firebase_service import delete_persona_chats
from backend.services.chat.pinecone_service import pinecone_delete_persona
from backend.funcs.users import (
    UserCRUDError,
    get_user_settings,
    update_user_settings
)
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/test')
def test():
    """Test route to check if server is working"""
    return render_template('test.html')

@main_bp.route('/')
def home():
    """Home page - Premium landing competing with Replika, Character.AI, Wysa"""
    # Render the premium landing page with carousel, floating CTA, social proof
    return render_template('index_premium.html')


@main_bp.route('/app')
@login_required
def app_main():
    """Main chat application page"""
    persona_query = request.args.get('persona')
    
    # Update persona if provided in URL
    if persona_query and current_user.is_authenticated:
        if not current_user.settings:
            current_user.settings = UserSettings(user_id=current_user.id)
            db.session.add(current_user.settings)
        current_user.settings.current_persona = persona_query.capitalize()
        db.session.commit()

    persona = get_persona()
    mode = get_mode()
    return render_template('chat.html', title='Chat • MyBella', persona=persona, mode=mode)

@main_bp.route('/settings', methods=['GET'])
@login_required
def settings():
    """User settings page"""
    # Ensure user has settings record
    if not current_user.settings:
        current_user.settings = UserSettings(user_id=current_user.id)
        db.session.add(current_user.settings)
        db.session.commit()

    # Prepare preferences with fallbacks
    prefs = {
        "persona": current_user.settings.current_persona or "Isabella",
        "mode": current_user.settings.mode or "Companion",
        "tts_enabled": current_user.settings.tts_enabled if current_user.settings.tts_enabled is not None else True,
        "voice_override": current_user.settings.voice_override or "",
        "age_confirmed": current_user.settings.age_confirmed if current_user.settings.age_confirmed is not None else False,
        "show_ads": current_user.settings.show_ads if current_user.settings.show_ads is not None else True
    }
    
    return render_template('settings.html', title='Settings • MyBella', prefs=prefs)

@main_bp.route('/api/prefs', methods=['POST'])
@login_required
def api_prefs():
    """Update user preferences"""
    settings_data = {
        'current_persona': (request.form.get('persona') or 'Isabella').capitalize(),
        'mode': request.form.get('mode') or 'Companion',
        'tts_enabled': True if request.form.get('tts_enabled') == 'on' else False,
        'voice_override': (request.form.get('voice_override') or '').strip() or None,
        'age_confirmed': True if request.form.get('age_confirmed') == 'on' else False,
        'show_ads': True if request.form.get('show_ads') == 'on' else False
    }
    
    try:
        success = update_user_settings(current_user.id, settings_data)
        if success:
            flash('Settings updated successfully!', 'success')
        else:
            flash('No changes were made to settings.', 'info')
    except UserCRUDError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash('An error occurred while updating settings.', 'danger')
    
    return redirect(url_for('main.settings'))

@main_bp.route('/api/persona/select', methods=['POST'])
@login_required
def api_persona_select():
    """Select active persona"""
    persona = (request.form.get('persona') or 'Isabella').capitalize()
    
    if not current_user.settings:
        current_user.settings = UserSettings(user_id=current_user.id)
        db.session.add(current_user.settings)
    
    current_user.settings.current_persona = persona
    db.session.commit()
    
    return redirect(url_for('main.app_main'))

@main_bp.route('/api/memory/reset', methods=['POST'])
@login_required
def api_memory_reset():
    """Reset memory for a specific persona"""
    user_id = str(current_user.id)
    persona = (request.form.get('persona') or get_persona()).capitalize()
    
    # Delete from Pinecone
    pinecone_delete_persona(user_id, persona)
    
    # Delete from Firestore
    delete_persona_chats(user_id, persona)
    
    flash(f"Reset memory for {persona}.", "info")
    return redirect(url_for('main.settings'))

@main_bp.route('/legal')
def legal():
    """Legal page"""
    return render_template('legal.html', title='Legal • MyBella')

@main_bp.route('/hotlines')
def hotlines():
    """Crisis hotlines page"""
    return render_template('hotlines.html', title='Hotlines • MyBella')

@main_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files (profile pictures, etc.)"""
    try:
        from flask import current_app
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        if upload_folder and os.path.exists(os.path.join(upload_folder, filename)):
            return send_from_directory(upload_folder, filename)
        else:
            # Return default avatar or 404
            return "File not found", 404
    except Exception:
        return "File not found", 404

# Template context processor
@main_bp.app_context_processor
def inject_user():
    """Inject current user into all templates"""
    return {"user": current_user}

@main_bp.route('/analytics')
@login_required
def analytics():
    """Analytics page - desktop only view"""
    # Basic analytics data
    analytics_data = {
        'total_chats': 0,
        'total_messages': 0,
        'favorite_persona': 'Bella',
        'usage_time': '0 hours',
        'active_days': 0
    }
    
    # You can add more complex analytics logic here
    return render_template('analytics.html', 
                         title='Analytics • MyBella', 
                         analytics=analytics_data)

@main_bp.route('/features')
def features():
    """Features page - showcasing app capabilities"""
    features_list = [
        {
            'title': 'AI Companions',
            'description': 'Engage with multiple AI personas tailored to your preferences',
            'icon': 'AI'
        },
        {
            'title': 'Voice Chat',
            'description': 'Natural voice conversations with your AI companions',
            'icon': 'Voice'
        },
        {
            'title': 'Smart Analytics',
            'description': 'Track your conversations and personal growth',
            'icon': 'Data'
        },
        {
            'title': 'Personalized Experience',
            'description': 'AI learns and adapts to your communication style',
            'icon': 'Personal'
        }
    ]
    
    return render_template('features.html', 
                         title='Features • MyBella', 
                         features=features_list)