"""
Firebase/Firestore service for MyBella
Handles document storage and retrieval from Firestore
"""

import logging
from flask import current_app

# Global Firestore client
fstore = None
firebase_ok = False

def initialize_firebase(app):
    """Initialize Firebase/Firestore client"""
    global fstore, firebase_ok
    
    try:
        firebase_project_id = app.config.get('FIREBASE_PROJECT_ID')
        firebase_client_email = app.config.get('FIREBASE_CLIENT_EMAIL')
        firebase_private_key = app.config.get('FIREBASE_PRIVATE_KEY')
        
        if firebase_project_id and firebase_client_email and firebase_private_key:
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            private_key = firebase_private_key.replace('\\n', '\n')
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": firebase_project_id,
                "private_key_id": "dummy",
                "private_key": private_key,
                "client_email": firebase_client_email,
                "client_id": "dummy",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{firebase_client_email}"
            })
            
            firebase_admin.initialize_app(cred)
            fstore = firestore.client()
            firebase_ok = True
            app.logger.info("Firebase initialized successfully")
        else:
            app.logger.warning("Firebase credentials incomplete, skipping initialization")
            
    except Exception as e:
        app.logger.warning(f"Firestore init skipped: {e}")
        firebase_ok = False

def store_message_firestore(user_id, persona, role, text):
    """Store a message in Firestore"""
    if not firebase_ok or not fstore:
        return
    
    try:
        collection_name = current_app.config.get('FIREBASE_DB_COLLECTION', 'mybella')
        fstore.collection(collection_name).document(user_id).collection("chats").add({
            "persona": persona,
            "role": role,
            "text": text
        })
    except Exception as e:
        current_app.logger.debug(f"Firestore store skip: {e}")

def get_persona_voice_id(user_id, persona):
    """Get voice ID for a specific persona from Firestore"""
    if not firebase_ok or not fstore:
        return None
    
    try:
        collection_name = current_app.config.get('FIREBASE_DB_COLLECTION', 'mybella')
        doc = fstore.collection(collection_name).document(user_id).collection("personas").document(persona.lower()).get()
        if doc and doc.exists:
            return doc.to_dict().get("voice_id")
    except Exception as e:
        current_app.logger.debug(f"Firestore persona voice fetch skip: {e}")
    
    return None

def set_persona_voice_id(user_id, persona, voice_id):
    """Set voice ID for a specific persona in Firestore"""
    if not firebase_ok or not fstore:
        return
    
    try:
        collection_name = current_app.config.get('FIREBASE_DB_COLLECTION', 'mybella')
        fstore.collection(collection_name).document(user_id).collection("personas").document(persona.lower()).set(
            {"voice_id": voice_id}, merge=True
        )
    except Exception as e:
        current_app.logger.debug(f"Firestore persona voice set skip: {e}")

def delete_persona_chats(user_id, persona):
    """Delete all chats for a specific persona from Firestore"""
    if not firebase_ok or not fstore:
        return
    
    try:
        collection_name = current_app.config.get('FIREBASE_DB_COLLECTION', 'mybella')
        chats = fstore.collection(collection_name).document(user_id).collection("chats").where("persona", "==", persona).stream()
        
        batch = fstore.batch()
        count = 0
        for chat in chats:
            batch.delete(chat.reference)
            count += 1
            if count % 400 == 0:
                batch.commit()
                batch = fstore.batch()
        batch.commit()
        
    except Exception as e:
        current_app.logger.debug(f"Firestore reset skip: {e}")

def get_firebase_status():
    """Get current Firebase connection status"""
    return firebase_ok