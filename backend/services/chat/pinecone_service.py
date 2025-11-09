"""
Pinecone vector database service for MyBella
Handles embeddings storage and retrieval for chat memory
"""

import logging
import requests
from flask import current_app

# Global Pinecone client and index
pc = None
index = None
pinecone_ok = False

def initialize_pinecone(app):
    """Initialize Pinecone client and index"""
    global pc, index, pinecone_ok
    
    try:
        pinecone_api_key = app.config.get('PINECONE_API_KEY')
        pinecone_env = app.config.get('PINECONE_ENV', 'us-east-1')
        pinecone_index_name = app.config.get('PINECONE_INDEX', 'mybella-memory')
        
        if pinecone_api_key:
            from pinecone import Pinecone, ServerlessSpec
            
            pc = Pinecone(api_key=pinecone_api_key)
            existing = [i["name"] for i in pc.list_indexes()]
            
            if pinecone_index_name not in existing:
                pc.create_index(
                    name=pinecone_index_name,
                    dimension=1536,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region=pinecone_env)
                )
            
            index = pc.Index(pinecone_index_name)
            pinecone_ok = True
            app.logger.info("Pinecone initialized successfully")
        else:
            app.logger.warning("Pinecone API key not provided, skipping initialization")
            
    except Exception as e:
        app.logger.warning(f"Pinecone init skipped: {e}")
        pinecone_ok = False

def embed_text(text):
    """Create text embedding using OpenAI API"""
    openai_api_key = current_app.config.get('OPENAI_API_KEY')
    if not openai_api_key:
        return None
    
    try:
        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "text-embedding-3-small",
            "input": text
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
        
    except Exception as e:
        current_app.logger.debug(f"Embed failed: {e}")
        return None

def pinecone_upsert(user_id, persona, text):
    """Store text embedding in Pinecone"""
    if not pinecone_ok or not index:
        return
    
    vec = embed_text(text)
    if not vec:
        return
    
    try:
        vector_id = f"{user_id}:{persona}:{str(abs(hash(text)))[:12]}"
        index.upsert([{
            "id": vector_id,
            "values": vec,
            "metadata": {
                "user_id": user_id,
                "persona": persona,
                "text": text
            }
        }])
    except Exception as e:
        current_app.logger.debug(f"Pinecone upsert skip: {e}")

def pinecone_delete_persona(user_id, persona):
    """Delete all vectors for a specific user and persona"""
    if not pinecone_ok or not index:
        return
    
    try:
        index.delete(filter={"user_id": user_id, "persona": persona})
    except Exception as e:
        current_app.logger.debug(f"Pinecone delete skip: {e}")

def retrieve_chunks(user_id, persona, query_text, top_k=5):
    """Retrieve relevant text chunks from Pinecone based on query"""
    chunks = []
    
    try:
        if pinecone_ok and current_app.config.get('OPENAI_API_KEY'):
            query_vector = embed_text(query_text)
            if not query_vector:
                return chunks
            
            result = index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True
            )
            
            # Handle both dict and object response formats
            matches = result.get('matches') if isinstance(result, dict) else getattr(result, 'matches', []) or []
            
            for match in matches:
                metadata = match.get("metadata", {})
                if (metadata.get("user_id") == user_id and 
                    metadata.get("persona", "").lower() == persona.lower()):
                    chunks.append(metadata.get("text", ""))
                    
    except Exception as e:
        current_app.logger.debug(f"Pinecone retrieve skip: {e}")
    
    return chunks[:top_k]

def get_pinecone_status():
    """Get current Pinecone connection status"""
    return pinecone_ok