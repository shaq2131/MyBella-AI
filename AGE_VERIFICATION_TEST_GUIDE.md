# 🚀 Age Verification Quick Test Guide

## Run Migration (If Not Already Done)

```bash
python scripts/migrations/add_age_verification.py
```

Expected output:
- ✅ Tables created
- ✅ 14 feature restrictions seeded
- ✅ 4 persona age configurations seeded

---

## Test Registration Flow

### Test Case 1: Minor (Blocked)
1. Navigate to `/register`
2. Enter username, email, gender
3. **Date of Birth**: Select a date that makes user 15 years old
4. Watch the age feedback appear in red: "❌ You must be at least 16 years old"
5. Submit button should be disabled
6. Try to submit → Error: "You must be at least 16 years old to use MyBella"

### Test Case 2: Teen Mode (16-17)
1. Navigate to `/register`
2. Enter username, email, gender
3. **Date of Birth**: Select a date that makes user 16 or 17 years old
4. Watch the age feedback appear in blue: "ℹ️ You'll access Teen Mode..."
5. Submit form
6. Should see welcome message: "Welcome to MyBella Teen Mode! Wellness tools, CBT exercises, and supportive companions."
7. Check dashboard → Should show teen-friendly features only

### Test Case 3: Adult Mode (18+)
1. Navigate to `/register`
2. Enter username, email, gender
3. **Date of Birth**: Select a date that makes user 18+ years old
4. Watch the age feedback appear in green: "✅ Full access to all features"
5. Submit form
6. Should see welcome message: "Welcome to MyBella! Enjoy full access to all features."
7. Check dashboard → Should show all features including romantic modes

---

## Test API Endpoints

### Check User's Age Status
```bash
# Login as test user, then:
curl http://localhost:5000/api/age-verification/status
```

Expected response:
```json
{
  "age": 16,
  "age_tier": "teen",
  "date_of_birth": "2008-01-15",
  "is_adult": false,
  "is_minor": false,
  "is_teen": true,
  "verified_at": "2025-01-15T10:30:00"
}
```

### Check Feature Access
```bash
# Teen user checking intimacy_mode (should be blocked):
curl http://localhost:5000/api/age-verification/feature-access/intimacy_mode

# Expected:
{
  "accessible": false,
  "feature_key": "intimacy_mode",
  "min_age_required": 18,
  "reason": "You must be 18+ to access Intimacy Mode"
}
```

```bash
# Teen user checking cbt_games (should be allowed):
curl http://localhost:5000/api/age-verification/feature-access/cbt_games

# Expected:
{
  "accessible": true,
  "feature_key": "cbt_games",
  "min_age_required": 16,
  "reason": null
}
```

### List Accessible Features
```bash
curl http://localhost:5000/api/age-verification/accessible-features
```

Expected for teen user:
```json
{
  "accessible_features": [
    "mood_letters",
    "cbt_games",
    "secrets_vault",
    "mood_timeline",
    "wellness_avatars",
    "study_companion",
    "voice_chat_basic",
    "unlimited_messages",
    "extra_cbt_packs",
    "streak_rewards"
  ]
}
```

### List Restricted Features
```bash
curl http://localhost:5000/api/age-verification/restricted-features
```

Expected for teen user:
```json
{
  "restricted_features": [
    {
      "compliance_reason": "Romantic content restricted for minors",
      "feature_key": "intimacy_mode",
      "feature_name": "Intimacy Mode",
      "min_age_required": 18,
      "years_until_access": 2
    },
    {
      "compliance_reason": "Romantic voice interactions restricted for minors",
      "feature_key": "whisper_talk",
      "feature_name": "WhisperTalk™",
      "min_age_required": 18,
      "years_until_access": 2
    },
    ...
  ]
}
```

### Check Persona Behavior
```bash
# Teen user checking Isabella (persona_id=1):
curl http://localhost:5000/api/age-verification/persona-behavior/1

# Expected:
{
  "allow_flirty_responses": false,
  "allow_romantic_dialogue": false,
  "persona_id": 1,
  "system_prompt": "You are Isabella, a supportive big sister figure...",
  "teen_forbidden_topics": ["romance", "dating", "intimacy"],
  "teen_tone": "supportive_sister",
  "wellness_focus_only": true
}
```

---

## Check Database

```bash
python -c "from backend import create_app; from backend.database.models.models import db; from backend.database.models.age_verification_models import *; app = create_app(); ctx = app.app_context(); ctx.push(); print(f'Features: {FeatureAccess.query.count()}'); print(f'Personas: {PersonaAgeRestriction.query.count()}'); print(f'Verifications: {UserAgeVerification.query.count()}')"
```

Expected:
```
Features: 14
Personas: 4
Verifications: [number of registered users]
```

---

## Verify Age Calculation

```bash
python test_age_verification_system.py
```

Expected output:
- ✅ Tables exist
- ✅ Age calculations correct
- ✅ Feature restrictions loaded
- ✅ Persona configurations loaded

---

## Visual Checks

### Registration Page
- [ ] DOB field present with calendar picker
- [ ] Max date set to today (can't select future dates)
- [ ] Age validation message appears below DOB field
- [ ] Message color changes based on age (red/blue/green)
- [ ] Submit button disabled when age invalid

### Dashboard (Teen User)
- [ ] No "Intimacy Mode" option visible
- [ ] No "WhisperTalk™" or romantic features
- [ ] CBT Games accessible
- [ ] Mood Timeline accessible
- [ ] Secrets Vault accessible
- [ ] Teen mode indicator visible (optional, future)

### Dashboard (Adult User)
- [ ] All features visible including romantic modes
- [ ] Intimacy Mode accessible
- [ ] WhisperTalk™ accessible
- [ ] Love Letters accessible
- [ ] No restrictions shown

---

## Troubleshooting

### Migration Issues
```bash
# If migration fails, check:
python -c "from backend import create_app; app = create_app(); print('App created successfully')"

# Check if models are imported:
python -c "from backend.database.models.age_verification_models import FeatureAccess; print('Models imported')"
```

### DOB Field Not Showing
- Check: `register.html` includes `<input type="date" id="date_of_birth" ...>`
- Check: `today_date` context variable passed in register() GET handler
- Clear browser cache

### Age Validation Not Working
- Open browser console (F12)
- Check for JavaScript errors
- Verify `validateAge()` function is defined
- Verify event listener attached to DOB field

### Backend Not Storing DOB
- Check: `user_auth.py` register() extracts `date_of_birth` from form
- Check: `AgeVerificationService.verify_age()` called after user creation
- Check: No exceptions in server logs
- Query database: `SELECT * FROM user_age_verification;`

---

## Success Indicators

✅ **Frontend**:
- DOB field renders with max date
- Real-time age validation shows correct messages
- Form submission blocked for under-16

✅ **Backend**:
- Registration creates User + UserAgeVerification records
- Age tier correctly calculated (minor/teen/adult)
- Age-appropriate welcome message displayed

✅ **Database**:
- 14 feature restrictions exist
- 4 persona age configurations exist
- User verification record created with correct age_tier

✅ **API**:
- `/api/age-verification/status` returns correct age info
- `/api/age-verification/feature-access/<key>` blocks teen-restricted features
- `/api/age-verification/persona-behavior/<id>` returns teen-appropriate settings

---

## Next Steps After Testing

1. **Integrate with Chat Service**
   - Inject age-appropriate system prompts
   - Filter romantic content for teen users

2. **Add Feature Access Middleware**
   - Protect intimacy routes with `@require_feature_access('intimacy_mode')`
   - Return 403 with age restriction message if blocked

3. **Create Teen Mode UI**
   - Add teen mode banner to dashboard
   - Show "locked" state for restricted features
   - Display "Available in X years" countdown

4. **Add Monetization**
   - Teen tier: $9.99/mo (wellness companion)
   - Adult tier: $14.99/mo (full features)
   - Payment integration with Stripe

---

*Quick test guide for age verification system. Start with registration flow, then API endpoints, then integration.* 🧪
