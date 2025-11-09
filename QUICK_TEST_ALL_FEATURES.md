# 🚀 QUICK TEST GUIDE - Verify All Features Work

## Step 1: Setup Secrets Vault (1 minute)

```bash
# Run this command to create the database table:
python scripts\migrations\add_secrets_vault.py
```

**Expected Output:**
```
🔐 Adding Secrets Vault table...
✅ secret_vault_entries table created successfully!
```

---

## Step 2: Start Server (1 command)

```bash
python test_startup.py
```

**Wait for:**
```
✅ MyBella server is running!
→ http://127.0.0.1:5000
```

---

## Step 3: Test Each Feature (10 minutes)

### ✅ Feature 1: CBT Games
**URL:** `http://localhost:5000/wellness/cbt/reframe-puzzle`

**What to Test:**
1. Click "Start Game" button
2. Drag a negative thought to the input
3. See the reframed positive thought
4. Complete all 5 thoughts
5. See your score and encouragement

**Success Criteria:** Game loads, drag works, score displays

---

**URL:** `http://localhost:5000/wellness/cbt/memory-match`

**What to Test:**
1. Click "Start Game"
2. Click two cards to flip
3. Match all pairs
4. See completion message

**Success Criteria:** Cards flip, matches detected, game completes

---

### ✅ Feature 2: Mood Tracking & Analytics
**URL:** `http://localhost:5000/wellness/mood-checkin`

**What to Test:**
1. Select a mood emoji
2. Choose emotions from the grid
3. Add optional notes
4. Submit check-in
5. See confirmation message

**Success Criteria:** Form submits, data saves, confirmation shows

---

**URL:** `http://localhost:5000/analytics`

**What to Test:**
1. See "Wellness Overview" stats
2. View mood trends chart (line graph)
3. View emotion distribution (pie chart)
4. View exercise statistics (bar chart)
5. Click "Weekly Report" button
6. Click "Export Data" button (downloads JSON)

**Success Criteria:** All charts render, data displays, export works

---

### ✅ Feature 3: Onboarding Quiz
**URL:** `http://localhost:5000/onboarding/quiz`

**What to Test:**
1. Answer all 10 questions
2. Click "See My Results"
3. View personalized wellness profile
4. See persona recommendations
5. Check "Your Wellness Priorities" section

**Success Criteria:** Quiz completes, results show, recommendations appear

---

### ✅ Feature 4: Age Verification
**Test via API (Terminal):**

```bash
# Check if age verification is set up for current user:
curl http://localhost:5000/api/age-verification/status
```

**Expected Response:**
```json
{
  "age_verified": true/false,
  "age_tier": "adult" or "teen",
  "user_age": 25
}
```

**Browser Test:**
- Visit: `http://localhost:5000/users/profile`
- Look for "Companion Mode" or "Teen Mode" badge
- Adult users (18+) see "Companion Mode"
- Teen users (16-17) see "Teen Mode"

**Success Criteria:** Age tier displays correctly based on DOB

---

### ✅ Feature 5: Memory Controls
**URL:** `http://localhost:5000/users/chat`

**What to Test:**
1. Look in **left sidebar** for "My Memories" section
2. See stats: "X Messages" and "Y Preferences"
3. Click **"👁️ View"** button → Modal shows recent conversations
4. Click **"💾 Export"** button → Downloads `mybella_memories_<user_id>_<date>.json`
5. Click **"🗑️ Delete"** button → 3 confirmations → Memories deleted

**Success Criteria:** 
- Stats update in real-time
- View modal shows messages
- Export downloads file
- Delete requires 3 confirmations

---

### ✅ Feature 6: Crisis Detection
**URL:** `http://localhost:5000/crisis/support`

**What to Test:**
1. See emergency buttons (988, 741741, 911)
2. Click a tel: link (should open phone app if on mobile)
3. Scroll to see all 5 hotlines
4. See reassurance messaging

**Success Criteria:** Page loads, links work, hotlines display

---

**Chat Integration Test:**
1. Go to: `http://localhost:5000/users/chat`
2. Type: "I'm feeling suicidal"
3. Send message

**Expected Behavior:**
- Crisis resources display automatically
- 988 hotline shown prominently
- Crisis Text Line shown
- Supportive message appears

**Success Criteria:** Crisis detected, resources shown, no regular AI response

---

### ✅ Feature 7: Secrets Vault (NEW!)
**URL:** `http://localhost:5000/secrets/vault`

**First Visit (PIN Setup):**
1. See "Set a 4-digit PIN" screen
2. Enter 4 digits (e.g., 1234)
3. Click "Set PIN"
4. Vault unlocks automatically

**Success Criteria:** PIN accepts 4 digits, vault unlocks

---

**Create Entry:**
1. Click "+ New Entry" button
2. Enter title: "Test Secret"
3. Enter content: "This is my private thought"
4. Select mood: "😊 Happy"
5. Click "Save"

**Success Criteria:** Entry saves, appears in card grid

---

**View Entry:**
1. Click on the entry card
2. See full content in modal
3. See mood and date

**Success Criteria:** Modal opens, full content displays

---

**Delete Entry:**
1. Click on entry card
2. Click "Delete" button
3. Confirm deletion
4. Entry disappears from grid

**Success Criteria:** Delete requires confirmation, entry removed

---

**Lock Vault:**
1. Click "🔒 Lock" button
2. Returns to PIN entry screen
3. Re-enter PIN to unlock

**Success Criteria:** Vault locks, requires PIN to re-enter

---

### ⚠️ Feature 8: Content Guardrails
**Status:** Not implemented yet (only database model exists)

**What Exists:**
- ContentModerationLog database table
- Age-appropriate system prompts

**What's Missing:**
- Active content filtering
- Profanity filter
- Moderation API

**To Test When Built:**
- Try sending inappropriate message in chat
- Should be blocked/filtered
- Log should be created in database

---

## Step 4: Run Full Test Suite (Optional)

```bash
# Test all features programmatically:
python test_secrets_vault.py
python test_mood_mirroring.py
python test_persona_system.py
python test_age_verification_system.py
```

**Expected:** All tests pass with ✅

---

## Step 5: Verify Database Tables

```bash
python -c "from backend import create_app; from backend.database.models.models import db; app=create_app(); app.app_context().push(); print('Tables:', db.engine.table_names())"
```

**Expected Tables to Exist:**
- `users`
- `mood_entries`
- `exercise_completions`
- `chat_messages`
- `onboarding_quiz`
- `age_verification`
- `feature_access`
- `secret_vault_entries` ← NEW!
- `content_moderation_log`

---

## 🎯 Success Checklist

After testing, you should have verified:

- [x] CBT Games load and work
- [x] Mood check-in saves data
- [x] Analytics dashboard shows charts
- [x] Onboarding quiz completes
- [x] Age verification displays correct tier
- [x] Memory controls view/export/delete
- [x] Crisis resources page loads
- [x] Crisis detection triggers in chat
- [x] **Secrets Vault PIN setup works**
- [x] **Secrets Vault creates/views/deletes entries**
- [ ] Content guardrails filter messages (not built yet)

**Score: 10/11 features working = 91% complete!**

---

## 🐛 Troubleshooting

### "Module not found" errors
```bash
# Install requirements:
pip install -r requirements.txt
```

### "Table doesn't exist" errors
```bash
# Create all tables:
python -c "from backend import create_app; from backend.database.models.models import db; app=create_app(); app.app_context().push(); db.create_all()"
```

### "Port 5000 already in use"
```bash
# Kill existing process (Windows):
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Secrets Vault "table not found"
```bash
# Run migration again:
python scripts\migrations\add_secrets_vault.py
```

---

## 📞 Quick Links

| Feature | URL |
|---------|-----|
| Dashboard | http://localhost:5000/users/dashboard |
| CBT Reframe Puzzle | http://localhost:5000/wellness/cbt/reframe-puzzle |
| CBT Memory Match | http://localhost:5000/wellness/cbt/memory-match |
| Mood Check-in | http://localhost:5000/wellness/mood-checkin |
| Analytics | http://localhost:5000/analytics |
| Onboarding Quiz | http://localhost:5000/onboarding/quiz |
| Chat (with Memory Controls) | http://localhost:5000/users/chat |
| Crisis Support | http://localhost:5000/crisis/support |
| **Secrets Vault** | http://localhost:5000/secrets/vault |

---

## ⏱️ Total Test Time: 15 minutes

**Breakdown:**
- Setup: 2 minutes
- Test each feature: 1-2 minutes each
- Verification: 2 minutes

**By the end, you'll have proof that 10/11 features work!** 🎉

---

*Ready to test? Start with Step 1!* 🚀
