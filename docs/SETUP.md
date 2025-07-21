# MyBella AI Setup Guide

This guide will help you set up MyBella AI from scratch, including all necessary API keys and configuration.

## 📋 Prerequisites

Before you begin, make sure you have:

- **Node.js 16+**: Download from [nodejs.org](https://nodejs.org/)
- **Git**: Download from [git-scm.com](https://git-scm.com/)
- **OpenAI Account**: Sign up at [platform.openai.com](https://platform.openai.com/)
- **ElevenLabs Account**: Sign up at [elevenlabs.io](https://elevenlabs.io/)

## 🔑 Getting API Keys

### OpenAI API Key

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Give it a name like "MyBella AI"
4. Copy the key and save it securely
5. **Important**: You need billing set up and credits available

### ElevenLabs API Key and Voice ID

1. Go to [ElevenLabs](https://elevenlabs.io/) and sign up
2. Navigate to your Profile → API Keys
3. Copy your API key
4. Go to VoiceLab → Voice Library
5. Choose a voice you like (recommended: "Bella" or similar female voice)
6. Click on the voice and copy the Voice ID from the URL or voice details

## 🚀 Installation Steps

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd mybella-ai

# Install all dependencies
npm run install:all
```

### 2. Environment Configuration

```bash
# Copy the environment template
cp .env.example .env

# Edit the .env file with your API keys
nano .env  # or use your preferred editor
```

Add your actual API keys:
```env
OPENAI_API_KEY=sk-your-actual-openai-key-here
ELEVENLABS_API_KEY=your-actual-elevenlabs-key-here
ELEVENLABS_VOICE_ID=your-chosen-voice-id-here
```

### 3. First Run

```bash
# Start the development server
npm run dev
```

This will:
- Start the backend server on port 3001
- Start the frontend React app on port 3000
- Open your browser automatically

## 🧪 Testing the Setup

1. **Backend Health Check**
   ```bash
   curl http://localhost:3001/api/health
   ```
   Should return: `{"status":"healthy","message":"MyBella AI Server is running"}`

2. **Frontend Access**
   - Open `http://localhost:3000` in your browser
   - You should see the MyBella AI interface
   - Try sending a message to test the chat functionality

3. **Voice Features**
   - Click the microphone button to test speech recognition
   - Enable audio to test text-to-speech responses

## 🔧 Troubleshooting

### Common Issues

#### "Invalid API Key" Error
- Double-check your OpenAI API key in the `.env` file
- Ensure you have billing set up on your OpenAI account
- Make sure there are no extra spaces in the API key

#### Voice Features Not Working
- Verify your ElevenLabs API key is correct
- Check that the Voice ID exists and is accessible
- Ensure your browser allows microphone access

#### Server Won't Start
- Check if ports 3000 and 3001 are available
- Run `npm run install:all` again to ensure all dependencies are installed
- Check the console for specific error messages

#### CORS Errors
- Ensure both frontend and backend are running
- Check that the `FRONTEND_URL` in `.env` matches your frontend URL

### Debugging Commands

```bash
# Check if dependencies are installed
npm list

# View server logs
cd server && npm run dev

# View client logs
cd client && npm start

# Test API endpoints
curl -X POST http://localhost:3001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Bella", "userId": "test"}'
```

## 🌐 Production Deployment

### Environment Variables for Production

```env
NODE_ENV=production
PORT=3001
FRONTEND_URL=https://your-domain.com
```

### Build and Deploy

```bash
# Build the frontend
npm run build

# Start production server
npm start
```

### Recommended Hosting Platforms

- **Vercel**: Great for the frontend (React app)
- **Railway**: Excellent for the backend (Node.js server)
- **Heroku**: Full-stack deployment
- **DigitalOcean**: VPS deployment with more control

## 🔒 Security Best Practices

1. **Never commit `.env` files** to version control
2. **Rotate API keys regularly**
3. **Use environment-specific configurations**
4. **Implement rate limiting** for production
5. **Add user authentication** if needed
6. **Monitor API usage** to avoid unexpected bills

## 📊 Monitoring and Analytics

### API Usage Monitoring

- **OpenAI**: Monitor usage at [platform.openai.com/usage](https://platform.openai.com/usage)
- **ElevenLabs**: Check usage in your ElevenLabs dashboard

### Application Monitoring

Consider adding:
- Error tracking (Sentry)
- Performance monitoring (New Relic)
- User analytics (Google Analytics)

## 🆙 Updating MyBella

```bash
# Pull latest changes
git pull origin main

# Update dependencies
npm run install:all

# Restart the application
npm run dev
```

## 📞 Support

If you encounter issues:

1. Check this documentation first
2. Look at the GitHub issues
3. Check the console logs for error messages
4. Ensure all API keys are valid and have sufficient credits

## 🎯 Next Steps

Once you have MyBella AI running:

1. **Customize Bella's personality** in `server/index.js`
2. **Modify the UI theme** in `client/src/App.tsx`
3. **Add new features** like conversation history, user profiles, etc.
4. **Deploy to production** using your preferred hosting platform

Happy chatting with Bella! 💖