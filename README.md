# MyBella • MVP v6 (Vercel-ready, Polished, Voice Cloning)
Flask app with OpenAI chat, ElevenLabs TTS (base64), **Voice Cloning upload**, Firestore, and Pinecone.
Runs in demo mode without keys. Add keys in `.env` to enable services.

## Quick Start (local)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python mybella/app.py
# open http://127.0.0.1:5000
