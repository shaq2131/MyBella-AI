import os
import json
import base64
import logging
from functools import wraps

from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, flash
)
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user
)
import requests

# --- Your models (SQLAlchemy) ---
from models import db, User, Chat, Message, UserSettings, init_db

# =========================
# App & Login setup
# =========================
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Core config
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")

    # Ensure instance path exists (for sqlite)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create instance path: {e}")

    # SQLite DB path inside instance/
    db_path = os.path.join(app.instance_path, 'mybella.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # API & feature config
    app.config.update(
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", ""),
        ELEVENLABS_API_KEY=os.getenv("ELEVENLABS_API_KEY", ""),
        ELEVENLABS_VOICE_ID=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
        FIREBASE_PROJECT_ID=os.getenv("FIREBASE_PROJECT_ID", ""),
        FIREBASE_CLIENT_EMAIL=os.getenv("FIREBASE_CLIENT_EMAIL", ""),
        FIREBASE_PRIVATE_KEY=os.getenv("FIREBASE_PRIVATE_KEY", ""),
        FIREBASE_DB_COLLECTION=os.getenv("FIREBASE_DB_COLLECTION", "mybella"),
        PINECONE_API_KEY=os.getenv("PINECONE_API_KEY", ""),
        PINECONE_ENV=os.getenv("PINECONE_ENVIRONMENT", "us-east-1"),
        PINECONE_INDEX=os.getenv("PINECONE_INDEX", "mybella-memory"),
        MAX_UPLOAD_MB=int(os.getenv("MAX_UPLOAD_MB", "10"))
    )

    app.config["MAX_CONTENT_LENGTH"] = app.config["MAX_UPLOAD_MB"] * 1024 * 1024

    # Login manager
    login_manager.login_view = 'login'           # redirects here when @login_required fails
    login_manager.login_message_category = 'info'

    # Attach SQLAlchemy & create tables
    init_db(app)

    # Init login manager
    login_manager.init_app(app)

    # Logging
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)

    return app

app = create_app()

# Make config globals
OPENAI_API_KEY = app.config['OPENAI_API_KEY']
ELEVENLABS_API_KEY = app.config['ELEVENLABS_API_KEY']
ELEVENLABS_VOICE_ID = app.config['ELEVENLABS_VOICE_ID']
FIREBASE_PROJECT_ID = app.config['FIREBASE_PROJECT_ID']
FIREBASE_CLIENT_EMAIL = app.config['FIREBASE_CLIENT_EMAIL']
FIREBASE_PRIVATE_KEY = app.config['FIREBASE_PRIVATE_KEY']
FIREBASE_DB_COLLECTION = app.config['FIREBASE_DB_COLLECTION']
PINECONE_API_KEY = app.config['PINECONE_API_KEY']
PINECONE_ENV = app.config['PINECONE_ENV']
PINECONE_INDEX = app.config['PINECONE_INDEX']

# Constants
ALLOWED_AUDIO_EXT = {".mp3", ".wav", ".m4a"}

# Flags
firebase_ok = False
pinecone_ok = False

# =========================
# Login loader (single)
# =========================
@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None

# =========================
# Firebase (Firestore) as fstore (avoid clobbering SQLAlchemy db)
# =========================
fstore = None
try:
    if FIREBASE_PROJECT_ID and FIREBASE_CLIENT_EMAIL and FIREBASE_PRIVATE_KEY:
        import firebase_admin
        from firebase_admin import credentials, firestore
        private_key = FIREBASE_PRIVATE_KEY.replace('\\n', '\n')
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": FIREBASE_PROJECT_ID,
            "private_key_id": "dummy",
            "private_key": private_key,
            "client_email": FIREBASE_CLIENT_EMAIL,
            "client_id": "dummy",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{FIREBASE_CLIENT_EMAIL}"
        })
        firebase_admin.initialize_app(cred)
        fstore = firestore.client()
        firebase_ok = True
except Exception as e:
    app.logger.warning(f"Firestore init skipped: {e}")
    firebase_ok = False

# =========================
# Pinecone
# =========================
pc = None
index = None
try:
    if PINECONE_API_KEY:
        from pinecone import Pinecone, ServerlessSpec
        pc = Pinecone(api_key=PINECONE_API_KEY)
        existing = [i["name"] for i in pc.list_indexes()]
        if PINECONE_INDEX not in existing:
            pc.create_index(
                name=PINECONE_INDEX,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV)
            )
        index = pc.Index(PINECONE_INDEX)
        pinecone_ok = True
except Exception as e:
    app.logger.warning(f"Pinecone init skipped: {e}")
    pinecone_ok = False

# =========================
# Helpers
# =========================
def _safe_filename(name):
    return "".join(c for c in name if c.isalnum() or c in ("_", "-", ".", " ")).strip()[:100]

def _allowed_audio(filename):
    import os as _os
    ext = _os.path.splitext(filename.lower())[1]
    return ext in ALLOWED_AUDIO_EXT

def get_user_id():
    # For non-auth parts; prefer flask-login where possible
    return str(current_user.id) if current_user.is_authenticated else (session.get("user_id") or "demo-user")

def get_persona():
    if current_user.is_authenticated and hasattr(current_user, "settings") and current_user.settings and current_user.settings.current_persona:
        return current_user.settings.current_persona
    return session.get("persona", "Isabella")

def get_mode():
    if current_user.is_authenticated and hasattr(current_user, "settings") and current_user.settings and current_user.settings.mode:
        return current_user.settings.mode
    return session.get("mode", "Companion")

def store_message_firestore(user_id, persona, role, text):
    if not firebase_ok or not fstore:
        return
    try:
        fstore.collection(FIREBASE_DB_COLLECTION).document(user_id).collection("chats").add({
            "persona": persona,
            "role": role,
            "text": text
        })
    except Exception as e:
        app.logger.debug(f"Firestore store skip: {e}")

def embed_text(text):
    if not OPENAI_API_KEY:
        return None
    try:
        url = "https://api.openai.com/v1/embeddings"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "text-embedding-3-small", "input": text}
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["data"][0]["embedding"]
    except Exception as e:
        app.logger.debug(f"Embed failed: {e}")
        return None

def pinecone_upsert(user_id, persona, text):
    if not pinecone_ok or not index:
        return
    vec = embed_text(text)
    if not vec:
        return
    try:
        _id = f"{user_id}:{persona}:{str(abs(hash(text)))[:12]}"
        index.upsert([{"id": _id, "values": vec, "metadata": {"user_id": user_id, "persona": persona, "text": text}}])
    except Exception as e:
        app.logger.debug(f"Pinecone upsert skip: {e}")

def pinecone_delete_persona(user_id, persona):
    if not pinecone_ok or not index:
        return
    try:
        index.delete(filter={"user_id": user_id, "persona": persona})
    except Exception as e:
        app.logger.debug(f"Pinecone delete skip: {e}")

def build_system_prompt(persona, mode, retrieved_chunks):
    base = f"You are {persona}, an empathetic AI companion in {mode} mode. Be concise, warm, and supportive."
    if mode == "Wellness":
        base += " Avoid romance or intimacy; focus on CBT-style reframing, journaling, and supportive check-ins."
    if retrieved_chunks:
        notes = "\n".join(f"- {c}" for c in retrieved_chunks)
        base += f"\nUse these remembered notes if relevant:\n{notes}"
    return base

def resolve_persona_voice_id(user_id, persona):
    # Env default
    voice_id = session.get("voice_override") or ELEVENLABS_VOICE_ID
    # Firestore persona voice
    try:
        if firebase_ok and fstore:
            doc = fstore.collection(FIREBASE_DB_COLLECTION).document(user_id).collection("personas").document(persona.lower()).get()
            if doc and doc.exists:
                vid = doc.to_dict().get("voice_id")
                if vid:
                    voice_id = vid
    except Exception:
        pass
    # Session cache fallback
    try:
        cache = session.get("voice_ids", {})
        vid2 = cache.get(persona.lower())
        if vid2:
            voice_id = vid2
    except Exception:
        pass
    return voice_id

def retrieve_chunks(user_id, persona, query_text):
    chunks = []
    try:
        if pinecone_ok and OPENAI_API_KEY:
            qvec = embed_text(query_text) or []
            if qvec:
                res = index.query(vector=qvec, top_k=5, include_metadata=True)
                matches = res.get('matches') if isinstance(res, dict) else getattr(res, 'matches', []) or []
                for m in matches:
                    md = m.get("metadata", {})
                    if md.get("user_id") == user_id and md.get("persona", "").lower() == persona.lower():
                        chunks.append(md.get("text", ""))
    except Exception:
        pass
    return chunks[:5]

# =========================
# Routes — Auth
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('app_main'))

    if request.method == 'POST':
        email = (request.form.get('email') or "").strip().lower()
        password = request.form.get('password') or ""
        remember = bool(request.form.get('remember'))

        try:
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user, remember=remember)
                flash('Successfully logged in!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page if next_page else url_for('app_main'))
            else:
                flash('Invalid email or password.', 'danger')
        except Exception as e:
            app.logger.error(f'Error during login: {str(e)}')
            flash('An error occurred during login. Please try again.', 'danger')

    return render_template('login.html', title='Sign In')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('app_main'))

    if request.method == 'POST':
        name = (request.form.get('name') or "").strip()
        email = (request.form.get('email') or "").strip().lower()
        password = request.form.get('password') or ""
        confirm_password = request.form.get('confirm_password') or ""
        terms = (request.form.get('terms') or "").lower()

        if not all([name, email, password, confirm_password, terms]):
            flash('All fields are required.', 'danger')
            return render_template('register.html', title='Create Account')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', title='Create Account')

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('register.html', title='Create Account')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return render_template('register.html', title='Create Account')

        if terms not in ('on', 'true', '1', 'yes'):
            flash('You must accept the terms of service.', 'danger')
            return render_template('register.html', title='Create Account')

        try:
            user = User(name=name, email=email)
            user.set_password(password)  # assumes your model method exists
            db.session.add(user)
            db.session.flush()  # get user.id

            settings = UserSettings(user_id=user.id)  # defaults from model
            db.session.add(settings)

            db.session.commit()
            app.logger.info(f'Successfully registered user: {email}')
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            import traceback
            db.session.rollback()
            app.logger.error(f'Registration error: {str(e)}')
            app.logger.error(f'Traceback: {traceback.format_exc()}')
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('register.html', title='Create Account')

    return render_template('register.html', title='Create Account')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# =========================
# Routes — App
# =========================
@app.route('/')
def home():
    return render_template('index.html', title='MyBella • MVP v6')

@app.route('/app')
@login_required
def app_main():
    persona_q = request.args.get('persona')
    if persona_q and current_user.is_authenticated:
        # persist persona choice to user settings if possible
        if not current_user.settings:
            current_user.settings = UserSettings(user_id=current_user.id)
            db.session.add(current_user.settings)
        current_user.settings.current_persona = persona_q.capitalize()
        db.session.commit()

    persona = get_persona()
    mode = get_mode()
    return render_template('chat.html', title='Chat • MyBella', persona=persona, mode=mode)

@app.route('/settings', methods=['GET'])
@login_required
def settings():
    # fallbacks if settings row missing
    if not current_user.settings:
        current_user.settings = UserSettings(user_id=current_user.id)
        db.session.add(current_user.settings)
        db.session.commit()

    prefs = {
        "persona": current_user.settings.current_persona or "Isabella",
        "mode": current_user.settings.mode or "Companion",
        "tts_enabled": current_user.settings.tts_enabled if current_user.settings.tts_enabled is not None else True,
        "voice_override": current_user.settings.voice_override or "",
        "age_confirmed": current_user.settings.age_confirmed if current_user.settings.age_confirmed is not None else False,
        "show_ads": current_user.settings.show_ads if current_user.settings.show_ads is not None else True
    }
    return render_template('settings.html', title='Settings • MyBella', prefs=prefs)

@app.route('/api/prefs', methods=['POST'])
@login_required
def api_prefs():
    s = current_user.settings or UserSettings(user_id=current_user.id)
    s.current_persona = (request.form.get('persona') or 'Isabella').capitalize()
    s.mode = request.form.get('mode') or 'Companion'
    s.tts_enabled = True if request.form.get('tts_enabled') == 'on' else False
    v_override = (request.form.get('voice_override') or '').strip()
    s.voice_override = v_override if v_override else None
    s.age_confirmed = True if request.form.get('age_confirmed') == 'on' else False
    s.show_ads = True if request.form.get('show_ads') == 'on' else False
    db.session.add(s)
    db.session.commit()
    return redirect(url_for('settings'))

@app.route('/api/persona/select', methods=['POST'])
@login_required
def api_persona_select():
    persona = (request.form.get('persona') or 'Isabella').capitalize()
    if not current_user.settings:
        current_user.settings = UserSettings(user_id=current_user.id)
        db.session.add(current_user.settings)
    current_user.settings.current_persona = persona
    db.session.commit()
    return redirect(url_for('app_main'))

@app.route('/api/memory/reset', methods=['POST'])
@login_required
def api_memory_reset():
    user_id = str(current_user.id)
    persona = (request.form.get('persona') or get_persona()).capitalize()
    # Pinecone purge
    pinecone_delete_persona(user_id, persona)
    # Firestore purge
    if firebase_ok and fstore:
        try:
            chats = fstore.collection(FIREBASE_DB_COLLECTION).document(user_id).collection("chats").where("persona", "==", persona).stream()
            batch = fstore.batch()
            count = 0
            for c in chats:
                batch.delete(c.reference); count += 1
                if count % 400 == 0: batch.commit(); batch = fstore.batch()
            batch.commit()
        except Exception as e:
            app.logger.debug(f"Firestore reset skip: {e}")
    flash(f"Reset memory for {persona}.", "info")
    return redirect(url_for('settings'))

@app.route('/legal')
def legal():
    return render_template('legal.html', title='Legal • MyBella')

@app.route('/hotlines')
def hotlines():
    return render_template('hotlines.html', title='Hotlines • MyBella')

# =========================
# API — Chat & TTS & Voice Upload
# =========================
def _system_and_chunks(user_text, persona, mode):
    user_id = get_user_id()
    chunks = retrieve_chunks(user_id, persona, user_text)
    sys = build_system_prompt(persona, mode, chunks)
    return sys, chunks

@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    data = request.get_json(force=True)
    user_text = (data.get('text') or '').strip()
    persona = (data.get('persona') or get_persona()).capitalize()
    mode = data.get('mode') or get_mode()
    if not user_text:
        return jsonify({"error": "Empty message"}), 400

    user_id = get_user_id()
    store_message_firestore(user_id, persona, "user", user_text)

    system_prompt, _ = _system_and_chunks(user_text, persona, mode)

    try:
        if not OPENAI_API_KEY:
            bot_text = f"(demo) {persona}: I hear you. Tell me more about how you're feeling."
        else:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
                "temperature": 0.7,
                "max_tokens": 250
            }
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            r.raise_for_status()
            bot_text = r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        app.logger.debug(f"Chat fallback: {e}")
        bot_text = "(demo) Sorry, I had trouble reaching the AI. Let's keep chatting."

    # Save convo (SQL/Firestore/Pinecone)
    try:
        db.session.add(Message(user_id=current_user.id, role="user", content=user_text, persona=persona))
        db.session.add(Message(user_id=current_user.id, role="bot", content=bot_text, persona=persona))
        db.session.commit()
    except Exception:
        db.session.rollback()
    pinecone_upsert(user_id, persona, user_text)
    pinecone_upsert(user_id, persona, bot_text)

    return jsonify({"text": bot_text})

@app.route('/api/tts', methods=['POST'])
@login_required
def api_tts():
    data = request.get_json(force=True)
    text = (data.get('text') or '').strip()
    persona = (data.get('persona') or get_persona()).capitalize()

    # Respect user setting (SQL-backed)
    tts_enabled = True
    if current_user.is_authenticated and current_user.settings and current_user.settings.tts_enabled is not None:
        tts_enabled = current_user.settings.tts_enabled
    if not tts_enabled:
        return jsonify({"audio_b64": None, "note": "(demo) TTS disabled in Settings."})

    user_id = get_user_id()
    voice_id = data.get('voice_id', resolve_persona_voice_id(user_id, persona))
    if not text:
        return jsonify({"error": "Empty text"}), 400

    try:
        if not ELEVENLABS_API_KEY:
            return jsonify({"audio_b64": None, "note": "(demo) Provide ELEVENLABS_API_KEY to enable audio."})
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
        payload = {"text": text, "model_id": "eleven_monolingual_v1", "voice_settings": {"stability": 0.5, "similarity_boost": 0.7}}
        r = requests.post(tts_url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        audio_b64 = base64.b64encode(r.content).decode('utf-8')
        return jsonify({"audio_b64": audio_b64})
    except Exception as e:
        app.logger.debug(f"TTS error: {e}")
        return jsonify({"error": str(e), "audio_b64": None}), 200

@app.route('/api/voice-upload', methods=['POST'])
@login_required
def api_voice_upload():
    if not ELEVENLABS_API_KEY:
        return jsonify({"ok": False, "error": "(demo) ELEVENLABS_API_KEY missing; cannot upload."}), 200

    persona = (request.form.get('persona') or get_persona()).capitalize()
    voice_name = (request.form.get('voice_name') or persona).strip()[:60]
    file = request.files.get('file')
    if not file or not getattr(file, 'filename', None):
        return jsonify({"ok": False, "error": "No file uploaded"}), 400

    filename = _safe_filename(file.filename)
    if not _allowed_audio(filename):
        return jsonify({"ok": False, "error": "Unsupported file type. Allowed: .mp3, .wav, .m4a"}), 400
    mimetype = file.mimetype or "audio/mpeg"

    try:
        url = "https://api.elevenlabs.io/v1/voices/add"
        headers = {"xi-api-key": ELEVENLABS_API_KEY}
        data = {"name": voice_name}

        r = requests.post(url, headers=headers, files={"files": (filename, file.stream, mimetype)}, data=data, timeout=120)
        voice_id = None
        try:
            resp = r.json(); voice_id = resp.get("voice_id") or resp.get("id")
        except Exception:
            resp = None

        if (r.status_code >= 400 or not voice_id):
            try: file.stream.seek(0)
            except Exception: pass
            r2 = requests.post(url, headers=headers, files={"file": (filename, file.stream, mimetype)}, data=data, timeout=120)
            try:
                resp = r2.json(); voice_id = resp.get("voice_id") or resp.get("id")
            except Exception:
                pass
            if r2.status_code >= 400 and not voice_id:
                return jsonify({"ok": False, "error": f"ElevenLabs error {r2.status_code}", "details": resp}), 200

        if not voice_id:
            try:
                lr = requests.get("https://api.elevenlabs.io/v1/voices", headers={"xi-api-key": ELEVENLABS_API_KEY}, timeout=60)
                lj = lr.json()
                for v in lj.get("voices", []):
                    if v.get("name") == voice_name:
                        voice_id = v.get("voice_id") or v.get("id")
                        break
            except Exception:
                pass

        if not voice_id:
            return jsonify({"ok": False, "error": "Could not determine new voice_id from ElevenLabs response."}), 200

        # Persist voice_id per user+persona (Firestore then session cache)
        user_id = get_user_id()
        try:
            if firebase_ok and fstore:
                fstore.collection(FIREBASE_DB_COLLECTION).document(user_id).collection("personas").document(persona.lower()).set({"voice_id": voice_id}, merge=True)
        except Exception:
            pass
        cache = session.get("voice_ids", {})
        cache[persona.lower()] = voice_id
        session["voice_ids"] = cache

        return jsonify({"ok": True, "voice_id": voice_id, "persona": persona})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 200

# =========================
# Template context
# =========================
@app.context_processor
def inject_user():
    return {"user": current_user}

# =========================
# Run
# =========================
if __name__ == '__main__':
    app.run(debug=True)
