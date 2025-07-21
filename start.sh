#!/bin/bash

# MyBella AI Startup Script
echo "🚀 Starting MyBella AI - Your Voice-Powered AI Companion"
echo "💖 Initializing servers..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before running the app"
    echo "   - Add your OpenAI API key"
    echo "   - Add your ElevenLabs API key"
    echo "   - Set your preferred ElevenLabs voice ID"
    exit 1
fi

# Start the application
echo "🌟 Starting MyBella AI servers..."
npm run dev