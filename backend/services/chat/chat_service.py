"""
Chat service for MyBella
Handles AI chat interactions, system prompts, and conversation logic
"""

import requests
from flask import current_app
from backend.services.chat.pinecone_service import retrieve_chunks
from backend.services.mood_service import MoodService

def build_system_prompt(persona, mode, retrieved_chunks=None, user_id=None):
    """
    Build system prompt for AI chat based on persona, mode, and user's mood
    
    Args:
        persona: Persona name (Isabella, Maya, Alex, etc.)
        mode: Chat mode (Wellness, Companion, etc.)
        retrieved_chunks: Memory chunks from vector database
        user_id: User ID for mood-aware tone adjustment
    
    Returns:
        str: Complete system prompt with mood-based tone adjustment
    """
    base_prompt = f"You are {persona}, an empathetic AI companion in {mode} mode. Be concise, warm, and supportive."
    
    if mode == "Wellness":
        base_prompt += " Avoid romance or intimacy; focus on CBT-style reframing, journaling, and supportive check-ins."
    
    if retrieved_chunks:
        notes = "\n".join(f"- {chunk}" for chunk in retrieved_chunks)
        base_prompt += f"\nUse these remembered notes if relevant:\n{notes}"
    
    # 🎭 MOOD-AWARE TONE ADJUSTMENT
    if user_id:
        base_prompt = MoodService.get_mood_adjusted_prompt(base_prompt, user_id)
    
    return base_prompt

def get_ai_response(user_text, persona, mode, user_id, persona_id=None):
    """
    Get AI response using OpenAI API with mood-aware tone adjustment
    
    Args:
        user_text: User's message
        persona: Persona name
        mode: Chat mode
        user_id: User ID
        persona_id: Persona ID for memory isolation
    
    Returns:
        str: AI response text
    """
    openai_api_key = current_app.config.get('OPENAI_API_KEY')
    
    if not openai_api_key:
        return f"(demo) {persona}: I hear you. Tell me more about how you're feeling."
    
    try:
        # Retrieve relevant memory chunks
        chunks = retrieve_chunks(user_id, persona, user_text)
        
        # Build mood-aware system prompt
        system_prompt = build_system_prompt(persona, mode, chunks, user_id=user_id)
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            "temperature": 0.7,
            "max_tokens": 250
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
        
    except Exception as e:
        current_app.logger.debug(f"Chat API error: {e}")
        return "(demo) Sorry, I had trouble reaching the AI. Let's keep chatting."