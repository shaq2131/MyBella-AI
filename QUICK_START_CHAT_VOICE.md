# 🚀 QUICK START GUIDE - Chat/Voice Mode & Memory Controls

## ✅ What's Ready

You now have a **production-grade Chat/Voice Mode Toggle** with smart API cost management and **Memory Controls** for users to manage their AI memories.

---

## 🎯 Start Testing in 3 Steps

### Step 1: Start the Server
```powershell
python test_startup.py
```

Wait for:
```
✅ App initialization successful!
   Access at: http://127.0.0.1:5000
```

### Step 2: Open Chat
Go to: **http://127.0.0.1:5000/users/chat**

(Login first if needed with any test account)

### Step 3: Test Features

#### Chat/Voice Toggle:
1. Look for the **💬 Chat** button (desktop: below input box, mobile: bottom-right floating)
2. Click to switch to **🎙️ Voice** mode
3. Type a message → AI will respond with voice (if ElevenLabs key set) or browser TTS
4. Switch back to **💬 Chat** → text only, no voice costs

#### Memory Controls:
1. Check the **🧠 My Memories** section in left sidebar
2. See live stats (Messages + Preferences count)
3. Click **👁️ View** → Modal with recent conversations
4. Click **💾 Export** → Downloads JSON file
5. Click **🗑️ Delete** → Triple confirmation, deletes all

---

## 💡 Key Features

### Smart Cost Management
- **Chat Mode (💬):** Text only → $0 API costs
- **Voice Mode (🎙️):** Voice responses → minutes deducted
- Users can toggle anytime based on their needs

### Mode Persistence
- Last used mode is remembered
- Auto-restores on next visit
- Saved per user in database

### Accessibility
- Voice mode ALWAYS shows text for reading
- Bella's avatar pulses when speaking
- High contrast, keyboard-friendly

### Memory Privacy
- Users see exactly what AI remembers
- Export for data portability
- Delete with triple confirmation for safety

---

## 🔧 Advanced Testing

### Test Voice Minutes Logic:

**In Chat Mode:**
```javascript
// Open browser console
// Type message → check response
// Verify: voice_used = false
// Verify: No minutes deducted
```

**In Voice Mode:**
```javascript
// Toggle to voice
// Type message → check response
// Verify: voice_used = true (or fallback reason)
// Verify: Minutes decrease (if ElevenLabs configured)
```

### Test Memory Controls:

1. Send some chat messages
2. Check sidebar stats update
3. View → see messages in modal
4. Export → verify JSON download
5. Delete → triple confirm → stats reset to 0

---

## 🎨 UI Behavior

### Desktop:
- Toggle button: Left side near input
- Memory widget: Sidebar, always visible
- Smooth animations on all interactions

### Mobile:
- Toggle button: Floating circle, bottom-right
- Memory widget: Collapsible in sidebar
- Touch-optimized 56px buttons

### Visual Feedback:
- Idle: Normal appearance
- Listening: Pulsing button
- Speaking: Glowing avatar border
- Mode switch: Notification toast

---

## 📊 What Gets Saved

### User Preferences Table:
```sql
user_settings:
  - preferred_chat_mode: 'chat' or 'voice'
  - (auto-loads on page refresh)
```

### Memory Data:
```sql
chat_messages:
  - All conversations
  - Timestamped
  - Persona-tagged

user_preferences:
  - Learned preferences
  - Category-organized
```

---

## 🐛 Troubleshooting

### Toggle not appearing?
- Clear browser cache
- Check console for JavaScript errors
- Verify blueprint registered: look for "user_prefs" in startup logs

### Voice not working?
- Expected if ELEVENLABS_API_KEY not set
- Falls back to browser TTS automatically
- Check browser console for errors

### Memory stats showing "–"?
- API may be loading
- Check network tab for `/api/memory/stats` call
- Verify user is logged in

### Mode not persisting?
- Check cookies enabled
- Verify login session active
- Look for `/api/user/chat-mode` POST in network tab

---

## 🎯 Success Criteria

✅ Toggle button visible and clickable  
✅ Mode icon switches (💬 ↔ 🎙️)  
✅ Voice mode plays audio (or browser TTS fallback)  
✅ Chat mode skips voice generation  
✅ Memory stats load and update  
✅ View shows conversations  
✅ Export downloads JSON  
✅ Delete requires triple confirmation  
✅ Mobile responsive (test on phone or DevTools)  

---

## 🚀 Next Steps (Optional)

After testing, you can enhance:

1. **Live Voice Input (STT):**
   - Add tap-and-hold to speak
   - Use Web Speech API for recognition
   - Stream to backend for processing

2. **Waveform Visualization:**
   - Show animated bars during voice playback
   - Real-time frequency analysis

3. **Advanced Memory Filters:**
   - Search by date range
   - Filter by persona
   - Selective deletion

4. **Voice Settings:**
   - Speed control (0.5x - 2x)
   - Pitch adjustment
   - Voice selection per persona

---

## 📞 Support

If something doesn't work:
1. Check browser console (F12)
2. Check server terminal for errors
3. Verify database migration ran
4. Test with a fresh user account

---

**Happy Testing! 🎉**

Everything is wired and ready. Start the server and explore your new features!

---

*Guide created: October 25, 2025*
