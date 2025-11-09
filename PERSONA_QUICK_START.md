# 🎭 Persona System - Quick Start Guide

## ⚡ Quick Setup (3 Steps)

### 1. Run Migration
```powershell
python scripts/migrations/add_persona_isolation.py
```
**What it does:** Adds persona_id columns, migrates existing data

### 2. Test Installation
```powershell
python test_persona_system.py
```
**Expected output:** "All systems operational!"

### 3. Start Server & Test
```powershell
python mybella.py
```
**Visit:** http://127.0.0.1:5000/users/personas

---

## 🎯 What You Built

✅ **Professional persona switcher** in settings (not top bar)  
✅ **Per-persona memory** - each persona remembers its own history  
✅ **Custom persona creation** - users design their own characters  
✅ **Voice customization** - ElevenLabs presets + custom uploads

---

## 📍 Key Files

### Backend
- `backend/routes/api/custom_persona_routes.py` - Persona management API
- `backend/database/models/models.py` - PersonaProfile with voice fields
- `backend/database/models/memory_models.py` - ChatMessage with persona_id
- `scripts/migrations/add_persona_isolation.py` - Database migration

### Frontend
- `frontend/templates/personas.html` - Persona management page
- Visit: `/users/personas` to access

---

## 🔗 API Endpoints

```
GET    /api/personas/available        - List all personas
POST   /api/personas/create           - Create custom persona
PUT    /api/personas/<id>             - Update custom persona
DELETE /api/personas/<id>             - Delete custom persona
POST   /api/personas/switch           - Switch active persona
GET    /api/personas/voice-presets    - List voice options
POST   /api/personas/<id>/voice/upload - Upload custom voice
```

---

## 🧪 Quick Test Checklist

1. **Migration:** Run script, see "Migration Complete"
2. **Access UI:** Visit `/users/personas`, see system personas
3. **Create Custom:** Click "Create", fill form, save
4. **Switch Persona:** Click "Select" on different persona
5. **Memory Test:** Chat with Persona A, switch to B, verify isolation
6. **Voice Test:** Edit persona, change voice preset, save

---

## 🎨 UI Features

### Current Persona
- Large gradient card at top
- Shows active persona with badge

### System Personas
- Card grid layout
- Each shows avatar, name, description
- "Select" button to switch

### Custom Personas
- Same layout as system
- "Edit" and "Delete" buttons
- Only visible to owner

### Create/Edit Modal
- Multi-section form
- Avatar upload with preview
- Voice preset dropdown
- Custom voice file upload

---

## 💡 Key Concepts

### Memory Isolation
Each persona has **separate conversation history**:
- Chat with Isabella → 10 messages
- Switch to Alex → Chat history empty
- Switch back to Isabella → 10 messages reappear

### Custom Personas
Users can create **unlimited custom personas**:
- Choose name, bio, personality traits
- Upload custom avatar
- Select voice from presets or upload custom
- Only visible to creator

### Voice System Priority
1. Custom uploaded voice file
2. ElevenLabs preset (voice_id)
3. Default system voice

---

## 🔧 Troubleshooting

### "Persona not found"
**Fix:** Run migration script

### Custom persona not appearing
**Fix:** Check `is_custom=1` in database

### Memory not isolated
**Fix:** Verify `persona_id` being saved with messages

### Voice not playing
**Fix:** Check ElevenLabs API key and voice_id

---

## 📚 Full Documentation

See **`PERSONA_SYSTEM_COMPLETE.md`** for:
- Complete architecture
- Database schema details
- API documentation
- Security considerations
- Performance tips
- User guide
- Developer guide

---

## ✨ Success!

You now have a **production-ready** persona management system with:
- Professional UI in settings
- True per-persona memory isolation
- Custom persona creation
- Voice customization
- Zero breaking changes to existing features

**Everything works without spoiling anything!** 🎉
