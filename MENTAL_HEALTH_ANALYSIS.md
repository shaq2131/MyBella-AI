# Mental Health Infrastructure Analysis

## 🎯 Executive Summary

**Status**: MyBella already has an **extensive, production-ready CBT system**. Rather than building from scratch, we will **integrate and enhance** existing features with:
1. Dynamic mood mirroring in chat AI
2. Persona integration with CBT exercises
3. Emotional memory timeline visualization
4. Unified mental health dashboard
5. Enhanced crisis detection with severity levels
6. Mental health awareness layer in conversations

---

## ✅ What Already Exists (DO NOT REBUILD)

### 1. **Database Models** (15 Models - `wellness_models.py`)

#### Core Wellness Models
- **`CBTSession`** - Full CBT therapy session tracking
  - Session type, persona, trigger events
  - Initial/final mood tracking
  - Automatic thoughts, thought patterns
  - Evidence for/against, balanced thoughts
  - Coping strategies, action plans
  - Homework assignments
  
- **`MoodEntry`** - Comprehensive daily mood tracking
  - Overall mood, anxiety, stress, energy levels
  - Sleep quality tracking
  - Exercise, water, meditation minutes
  - Social interaction tracking
  - Gratitude notes, reflections, challenges
  - Date-stamped entries with user relationship

- **`WellnessGoal`** - Goal setting and progress tracking
  - Categories: mental_health, physical, relationships, career, financial, personal_growth
  - Target dates, measurable goals
  - Progress percentage tracking
  - Milestone system
  - Completion status

- **`FinanceEntry`** - Financial wellness tracking
  - Transaction types (income/expense)
  - Budget categories
  - Spending mood analysis
  - Necessity ratings, regret levels
  - Financial stress correlation

- **`SocialConnection`** - Relationship management
  - Relationship types (family, friend, partner, colleague, mentor)
  - Contact frequency tracking
  - Quality ratings
  - Last contact dates
  - Personal notes

- **`CopingStrategy`** - Personalized coping techniques
  - Categories (breathing, meditation, exercise, social, creative)
  - Difficulty levels (1-5)
  - Usage tracking (times used)
  - Effectiveness ratings
  - Trigger situations
  - Personal modifications
  - AI recommendations

- **`WellnessInsight`** - AI-generated insights
  - Insight types (mood_pattern, coping_success, goal_milestone, wellness_tip)
  - Priority levels
  - View tracking
  - Helpful ratings

#### CBT Game Models (Interactive Tools)
- **`ThoughtReframe`** - Reframe Puzzle game
  - Negative thought capture
  - Cognitive distortion detection (10 types)
  - User reframes with AI feedback
  - Alternative reframes suggestions
  - Quality scoring (1-10) + creativity bonuses
  - Points system, completion tracking

- **`EmotionMatch`** - Memory Match game
  - Emotion-coping strategy pairs
  - Difficulty levels (easy/medium/hard)
  - Time tracking, accuracy scoring
  - Matches completed, attempts tracking
  - Points based on time and accuracy

- **`DailyNote`** - Journaling with CBT prompts
  - Note types (general, gratitude, challenge, goal, emotion)
  - 20+ therapeutic prompts
  - AI persona responses
  - Mood before/after tracking
  - Tags system
  - Privacy controls (private, pinned)

- **`LoveLetter`** - Emotional journaling (18+ Companion Mode)
  - To/from persona direction
  - Emotional themes (love, gratitude, vulnerability, joy)
  - Intensity levels (1-10)
  - Read tracking, favorites
  - Persona-specific letters

- **`WellnessRoutine`** - Daily routine builder
  - Routine types (morning, evening, custom)
  - Task lists (JSON array)
  - Reminder times
  - Streak tracking (current + longest)
  - Last completion dates

- **`RoutineCompletion`** - Routine tracking
  - Completion dates/times
  - Tasks completed (JSON)
  - Completion percentage
  - Mood ratings after completion
  - Notes

- **`WellnessAchievement`** - Badge system
  - Achievement types (first_steps, week_warrior, mind_master, goal_crusher, wellness_champion)
  - Points (10-200)
  - Unlock requirements
  - Special rewards
  - Date unlocked

- **`CheckInEntry`** - Morning/evening check-ins
  - Check-in types (morning/evening)
  - Sleep quality tracking
  - Morning mood, intentions, affirmations
  - Evening mood, gratitude, accomplishments
  - Challenges faced

### 2. **Backend Services** (591 Lines - `cbt_games_service.py`)

#### ReframePuzzleService
- `create_reframe_puzzle()` - Generate scenarios with negative thoughts
- `submit_reframe()` - Score reframes 1-10 based on quality
- `detect_distortion()` - Identify 10 cognitive distortion types
- `generate_feedback()` - Provide encouraging AI feedback
- Points system: Base score + creativity bonus

#### MemoryMatchService
- `start_game()` - Create emotion-coping strategy pairs
- `complete_game()` - Calculate score (time-based + accuracy)
- Difficulty scaling: Easy (6 pairs), Medium (8), Hard (10)
- Pair generation for 8 emotion categories

#### DailyNoteService
- `get_cbt_prompt()` - 20+ therapeutic prompts by category
- `create_note()` - Save with mood tracking and privacy settings
- `get_ai_response()` - Generate empathetic persona responses
- Categories: General, Gratitude, Challenge, Goal, Emotion, Affirmation

#### CheckInService
- `morning_checkin()` - Sleep quality, daily intention, affirmations
- `evening_checkin()` - Gratitude, accomplishments, challenges
- Persona-based responses (Isabella, Maya, Alex)
- Personalized AI messages based on check-in data

#### AchievementService
- `check_achievements()` - Auto-unlock based on activity
- `get_user_achievements()` - Progress tracking
- 5 achievement tiers with increasing points
- Badge unlocking system

### 3. **API Routes** (366 Lines - `cbt_games_routes.py`)

#### Reframe Puzzle Routes (5 endpoints)
- `GET /wellness/games/reframe` - Game page
- `POST /wellness/games/reframe/start` - Start new puzzle
- `POST /wellness/games/reframe/submit` - Submit reframe with scoring
- Achievement integration on completion

#### Memory Match Routes (5 endpoints)
- `GET /wellness/games/memory-match` - Game page
- `POST /wellness/games/memory-match/start` - Create new game
- `POST /wellness/games/memory-match/complete` - Finish game with scoring

#### Daily Notes Routes (4 endpoints)
- `GET /wellness/games/daily-notes` - Notes page
- `POST /wellness/games/daily-notes/create` - Create note
- `GET /wellness/games/daily-notes/history` - View past notes
- Full CRUD for journaling

#### Check-in Routes (4 endpoints)
- `GET /wellness/games/checkin` - Check-in page
- `POST /wellness/games/checkin/morning` - Morning check-in
- `POST /wellness/games/checkin/evening` - Evening check-in
- Persona responses integrated

#### Achievement Routes (2 endpoints)
- `GET /wellness/games/achievements` - Achievements page
- `GET /wellness/games/achievements/progress` - Progress API

### 4. **Wellness Services** (`wellness_services.py`)

#### CBTService
- Session management (start, update, complete)
- Progress tracking and analytics
- Thought pattern analysis
- Coping strategy recommendations

#### MoodTrackingService
- Mood entry creation and retrieval
- Trend analysis (7-day, 30-day, 90-day)
- Pattern detection
- Correlation analysis (sleep, exercise, mood)

#### GoalTrackingService
- Goal CRUD operations
- Progress calculation
- Milestone tracking
- Completion detection

#### FinanceWellnessService
- Financial tracking
- Budget analysis
- Spending pattern detection
- Financial stress correlation with mood

### 5. **Mood Tracking Routes** (`mood_routes.py`)

- `GET /mood/checkin` - Daily mood check-in page
- `POST /mood/api/submit` - Submit mood with achievement tracking
- `GET /mood/journal` - View past 30 days of entries
- `GET /mood/insights` - Mood analytics and patterns
- Integration with AchievementsService for streak tracking

### 6. **Exercise Routes** (`exercises_routes.py`)

- `GET /exercises/` - Exercise hub with stats
- `GET /exercises/breathing` - Breathing exercises overview
- `GET /exercises/breathing/<name>` - Specific exercises (4-7-8, box, calm)
- `GET /exercises/meditation` - Meditation sessions
- `GET /exercises/journaling` - Journaling prompts with categories
- `POST /exercises/api/complete` - Track completion with achievements

### 7. **Crisis Detection Service** (`crisis_detection.py`)

- **CRISIS_KEYWORDS**: 50+ crisis indicators
  - Suicide ideation keywords
  - Self-harm indicators
  - Severe distress markers
  - Planning indicators
  - Abuse indicators

- **CRISIS_PATTERNS**: Regex patterns for complex detection
  - Intent detection patterns
  - Context-aware phrase matching

- **CRISIS_RESOURCES**: Comprehensive support resources
  - 988 Suicide & Crisis Lifeline
  - Crisis Text Line (741741)
  - National Domestic Violence Hotline
  - SAMHSA National Helpline
  - Veterans Crisis Line
  - Online resources (IASP, NAMI)

- `detect_crisis()` function returns:
  - Boolean: Is crisis detected?
  - Severity level string
  - List of matched indicators

### 8. **Frontend Templates** (Existing)

- `frontend/templates/wellness/`
  - `hub.html` - CBT games hub
  - `reframe_puzzle.html` - Thought reframing game
  - `memory_match.html` - Emotion-coping game
  - `daily_notes.html` - Journaling interface
  - `checkin.html` - Morning/evening check-ins
  - `achievements.html` - Badge showcase

- `frontend/templates/mood/`
  - `checkin.html` - Mood check-in form
  - `journal.html` - Mood history view
  - `insights.html` - Mood analytics

- `frontend/templates/exercises/`
  - `index.html` - Exercise hub
  - `breathing.html` - Breathing exercises
  - `breathing_exercise.html` - Individual exercise pages
  - `meditation.html` - Meditation sessions
  - `journaling.html` - Journaling prompts

---

## 🚧 What Needs to Be Built (Integration & Enhancement)

### 1. **Dynamic Mood Mirroring in Chat AI** ⏳
**Location**: `backend/services/chat/chat_service.py` or voice_chat_service.py

**What to Add**:
- Accept `mood_context` parameter in chat/voice functions
- Query most recent `MoodEntry` for user
- Map mood to tone adjustments:
  - **Stressed/Anxious (1-3)**: Gentle, calming, reassuring tone
  - **Low/Below Average (4-5)**: Supportive, empathetic, encouraging
  - **Average (6)**: Balanced, conversational
  - **Good/Very Good (7-8)**: Upbeat, energetic, motivational
  - **Excellent/Outstanding (9-10)**: Enthusiastic, celebratory

**Implementation**:
```python
def get_mood_adjusted_system_prompt(user_id, base_prompt):
    """Adjust AI system prompt based on user's current mood"""
    today = date.today()
    recent_mood = MoodEntry.query.filter(
        MoodEntry.user_id == user_id,
        MoodEntry.entry_date >= today - timedelta(days=1)
    ).order_by(MoodEntry.entry_date.desc()).first()
    
    if not recent_mood:
        return base_prompt
    
    mood_level = recent_mood.overall_mood.value
    
    if mood_level <= 3:
        tone_adjustment = "Use a gentle, calming tone. Be extra supportive and reassuring."
    elif mood_level <= 5:
        tone_adjustment = "Be empathetic and encouraging. Focus on positivity."
    elif mood_level <= 6:
        tone_adjustment = "Maintain a balanced, conversational tone."
    elif mood_level <= 8:
        tone_adjustment = "Be upbeat and energetic. Share in their positivity."
    else:
        tone_adjustment = "Be enthusiastic and celebratory! Match their great mood."
    
    return f"{base_prompt}\n\n{tone_adjustment}"
```

### 2. **Persona Integration with CBT Exercises** ⏳
**Files to Modify**:
- `backend/database/models/wellness_models.py` (add persona_id columns)
- `backend/services/cbt_games_service.py` (accept persona_id in all create functions)
- `backend/routes/wellness/cbt_games_routes.py` (pass current persona to services)

**Database Migration**:
```python
# Add persona_id to CBT models for continuity
ALTER TABLE thought_reframes ADD COLUMN persona_id INTEGER;
ALTER TABLE daily_notes ADD COLUMN persona_id INTEGER;
ALTER TABLE checkin_entries ADD COLUMN persona_id INTEGER;
ALTER TABLE cbt_sessions ADD COLUMN persona_id INTEGER;

# Foreign key relationships
ALTER TABLE thought_reframes ADD FOREIGN KEY(persona_id) REFERENCES persona_profiles(id);
# ... repeat for other tables
```

**Service Updates**:
```python
# In ReframePuzzleService.create_reframe_puzzle()
def create_reframe_puzzle(user_id, negative_thought, persona_id=None):
    puzzle = ThoughtReframe(
        user_id=user_id,
        negative_thought=negative_thought,
        persona_id=persona_id  # NEW: Track which persona guided this
    )
    # ... rest of logic

# In DailyNoteService.create_note()
def create_note(user_id, content, persona_id=None):
    note = DailyNote(
        user_id=user_id,
        content=content,
        persona_id=persona_id  # NEW: Remember persona context
    )
    # ... AI response uses persona voice
```

**Impact**: CBT exercises will remember which persona guided the session, providing continuity in therapeutic relationships.

### 3. **Emotional Memory Timeline UI** 🎨
**New File**: `frontend/templates/wellness/timeline.html`
**New Route**: `/wellness/timeline` in wellness_routes.py
**New Service**: Timeline data aggregation function

**Features to Build**:
- **Visual Timeline** (scrollable, responsive)
  - Mood graph (line chart) showing trends over 30/60/90 days
  - Milestone markers (first reframe, 10-day streak, goal completed)
  - Achievement badges displayed on unlock dates
  - CBT session markers with session types
  - Crisis event markers (if any) with follow-up notes

- **Filters**:
  - Date range selector (7 days, 30 days, 90 days, all time)
  - Event type filters (mood, achievements, CBT, check-ins)
  - Mood level filters (show only low days, high days)

- **Insights Panel**:
  - AI-generated observations: "Your mood improved 40% after starting daily check-ins"
  - Pattern detection: "You tend to feel better on days with exercise"
  - Progress highlights: "You've completed 15 thought reframes this month!"
  - Milestone celebrations: "🎉 30-day wellness streak!"

**Data Aggregation Function**:
```python
def get_emotional_timeline(user_id, days=30):
    """Aggregate all wellness data for timeline visualization"""
    start_date = date.today() - timedelta(days=days)
    
    # Get mood entries
    moods = MoodEntry.query.filter(
        MoodEntry.user_id == user_id,
        MoodEntry.entry_date >= start_date
    ).order_by(MoodEntry.entry_date).all()
    
    # Get achievements
    achievements = WellnessAchievement.query.filter(
        WellnessAchievement.user_id == user_id,
        WellnessAchievement.created_at >= start_date
    ).all()
    
    # Get CBT sessions
    cbt_sessions = CBTSession.query.filter(
        CBTSession.user_id == user_id,
        CBTSession.created_at >= start_date
    ).all()
    
    # Get check-ins
    checkins = CheckInEntry.query.filter(
        CheckInEntry.user_id == user_id,
        CheckInEntry.checkin_date >= start_date
    ).all()
    
    # Get thought reframes
    reframes = ThoughtReframe.query.filter(
        ThoughtReframe.user_id == user_id,
        ThoughtReframe.created_at >= start_date,
        ThoughtReframe.completed == True
    ).all()
    
    return {
        'mood_data': [{'date': m.entry_date, 'mood': m.overall_mood.value, 'anxiety': m.anxiety_level.value if m.anxiety_level else None} for m in moods],
        'milestones': [
            {'date': a.created_at, 'type': 'achievement', 'title': a.achievement_type, 'points': a.points_earned} for a in achievements
        ] + [
            {'date': s.created_at, 'type': 'cbt_session', 'title': f"CBT: {s.session_type}"} for s in cbt_sessions
        ] + [
            {'date': r.created_at, 'type': 'reframe', 'title': f"Reframed thought (+{r.total_points} pts)"} for r in reframes
        ],
        'check_ins': [{'date': c.checkin_date, 'type': c.checkin_type, 'morning_mood': c.morning_mood, 'evening_mood': c.evening_mood} for c in checkins],
        'insights': generate_timeline_insights(moods, achievements, cbt_sessions)
    }
```

### 4. **Mental Health Dashboard Hub** 🏠
**File**: Enhance existing `/wellness` route in `wellness_routes.py`
**Template**: Update `frontend/templates/wellness/wellness_dashboard.html`

**Dashboard Sections**:
1. **Current Mood Widget**
   - Today's mood if entered
   - Quick mood check-in button
   - Mood trend indicator (↑ improving, → stable, ↓ declining)

2. **Wellness Streak Card**
   - Current streak count (days)
   - Longest streak badge
   - Next milestone countdown
   - Streak calendar visualization

3. **Quick Access Cards**
   - "Start Reframe Puzzle" card (icon + description)
   - "Daily Check-in" card (morning/evening)
   - "Write in Journal" card
   - "Play Memory Match" card

4. **Emotional Timeline Preview**
   - Mini graph of last 7 days mood
   - "View Full Timeline" link

5. **Recent Achievements**
   - Last 3 unlocked badges
   - Total points display
   - Next achievement progress bar

6. **Crisis Resources Sidebar**
   - Always visible on dashboard
   - 988 Suicide & Crisis Lifeline (prominent)
   - Crisis Text Line
   - "I need support now" button (opens full resources)

7. **Progress Metrics**
   - Total CBT sessions completed
   - Thought reframes count
   - Journal entries written
   - Check-ins completed
   - Days since joining

**Layout**: Clean card-based grid, mobile-responsive, gradient accents matching persona system design.

### 5. **Enhanced Crisis Detection with Priority System** 🚨
**File**: Enhance `backend/services/crisis_detection.py`

**Add Severity Levels**:
```python
class CrisisSeverity(enum.Enum):
    LOW = 1          # Mild distress, general stress
    MEDIUM = 2       # Moderate concern, emotional pain
    HIGH = 3         # Serious concern, ideation without plan
    CRITICAL = 4     # Immediate danger, plan or intent

def detect_crisis_with_severity(message: str) -> Dict:
    """Enhanced detection with severity classification"""
    
    # Check for critical keywords (suicide plan, imminent harm)
    critical_keywords = ['tonight', 'right now', 'about to', 'goodbye world', 'final message']
    if any(word in message.lower() for word in critical_keywords):
        severity = CrisisSeverity.CRITICAL
    
    # Check for high severity (ideation, self-harm)
    high_keywords = ['kill myself', 'end my life', 'suicide', 'hurt myself']
    elif any(word in message.lower() for word in high_keywords):
        severity = CrisisSeverity.HIGH
    
    # Check for medium severity (distress, hopelessness)
    medium_keywords = ['hopeless', 'worthless', 'can\'t go on', 'give up']
    elif any(word in message.lower() for word in medium_keywords):
        severity = CrisisSeverity.MEDIUM
    
    else:
        severity = CrisisSeverity.LOW
    
    return {
        'is_crisis': True,
        'severity': severity,
        'intervention_strategy': get_intervention_strategy(severity),
        'resources': get_resources_by_severity(severity),
        'should_log': severity >= CrisisSeverity.MEDIUM,
        'requires_human_review': severity >= CrisisSeverity.HIGH
    }

def get_intervention_strategy(severity: CrisisSeverity) -> str:
    """Get appropriate intervention based on severity"""
    strategies = {
        CrisisSeverity.CRITICAL: "IMMEDIATE: Display 988 prominently, pause conversation, offer immediate connection options.",
        CrisisSeverity.HIGH: "URGENT: Show crisis resources, encourage professional help, gentle check-in.",
        CrisisSeverity.MEDIUM: "SUPPORTIVE: Offer coping strategies, suggest mood check-in, gentle resource mention.",
        CrisisSeverity.LOW: "GENTLE: Continue supportive conversation, note for follow-up, wellness reminder."
    }
    return strategies[severity]
```

**Crisis Event Logging**:
```python
class CrisisEvent(db.Model):
    """Log crisis detections for follow-up and safety tracking"""
    __tablename__ = 'crisis_events'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    severity = db.Column(db.Enum(CrisisSeverity))
    message_snippet = db.Column(db.Text)  # Sanitized snippet
    keywords_matched = db.Column(db.Text)  # JSON list
    resources_shown = db.Column(db.Text)  # JSON list
    user_response = db.Column(db.Text)  # Did they engage with resources?
    follow_up_needed = db.Column(db.Boolean, default=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### 6. **Mental Health Awareness Layer in Chat** 💬
**Files to Modify**:
- `backend/routes/api/chat_routes.py` (add crisis scanning)
- `backend/services/chat/chat_service.py` (integrate crisis detection)
- `frontend/static/js/chat.js` (handle crisis UI)

**Chat Flow Integration**:
```python
# In chat_routes.py or voice_chat_service.py
from backend.services.crisis_detection import detect_crisis_with_severity

def api_chat():
    user_message = request.json.get('message')
    
    # 1. Scan for crisis indicators
    crisis_result = detect_crisis_with_severity(user_message)
    
    if crisis_result['is_crisis'] and crisis_result['severity'] >= CrisisSeverity.MEDIUM:
        # Log the event
        crisis_event = CrisisEvent(
            user_id=current_user.id,
            severity=crisis_result['severity'],
            message_snippet=user_message[:200],  # First 200 chars
            keywords_matched=json.dumps(crisis_result['matched_keywords']),
            resources_shown=json.dumps(crisis_result['resources'])
        )
        db.session.add(crisis_event)
        db.session.commit()
        
        # Modify AI response to be supportive
        system_prompt = f"""
        {base_persona_prompt}
        
        IMPORTANT: The user may be in emotional distress. Be gentle, validating, and supportive.
        Do not ignore their feelings. Acknowledge their pain with empathy.
        After your response, resources will be shown, so focus on emotional support.
        """
    
    # 2. Get mood-adjusted prompt
    system_prompt = get_mood_adjusted_system_prompt(current_user.id, system_prompt)
    
    # 3. Generate AI response
    ai_response = generate_chat_response(user_message, system_prompt)
    
    # 4. Return with crisis resources if needed
    return jsonify({
        'response': ai_response,
        'crisis_detected': crisis_result['is_crisis'],
        'show_resources': crisis_result['severity'] >= CrisisSeverity.MEDIUM,
        'resources': crisis_result['resources'] if crisis_result['is_crisis'] else None
    })
```

**Frontend Crisis UI**:
```javascript
// In chat.js - handle crisis resource display
if (response.crisis_detected && response.show_resources) {
    // Show gentle, non-intrusive resource card below AI message
    const resourceCard = `
        <div class="crisis-resource-card">
            <div class="resource-icon">💙</div>
            <h4>You're Not Alone</h4>
            <p>If you're in crisis, free support is available 24/7:</p>
            <ul>
                <li><strong>988</strong> - Suicide & Crisis Lifeline</li>
                <li><strong>Text HOME to 741741</strong> - Crisis Text Line</li>
            </ul>
            <button onclick="showFullResources()">View All Resources</button>
        </div>
    `;
    // Append below AI response without disrupting conversation flow
}
```

**Subtle Wellness Reminders**:
- After 30 minutes of conversation: "Would you like to take a mood check-in?"
- After difficult topic: "I'm here for you. Would you like to try a calming breathing exercise?"
- Before ending session: "Remember to practice self-compassion today 💙"

### 7. **Database Migration for Persona-CBT Integration** 📊
**New File**: `scripts/migrations/add_persona_to_cbt.py`

```python
"""
Add persona_id to CBT and wellness models for persona continuity
"""
from backend import create_app
from backend.database.models.models import db
from sqlalchemy import text

def migrate_persona_cbt():
    """Add persona_id columns to CBT models"""
    app, socketio = create_app()
    
    with app.app_context():
        with db.engine.connect() as conn:
            # Add persona_id to thought_reframes
            conn.execute(text("""
                ALTER TABLE thought_reframes 
                ADD COLUMN persona_id INTEGER;
            """))
            
            # Add persona_id to daily_notes
            conn.execute(text("""
                ALTER TABLE daily_notes 
                ADD COLUMN persona_id INTEGER;
            """))
            
            # Add persona_id to checkin_entries
            conn.execute(text("""
                ALTER TABLE checkin_entries 
                ADD COLUMN persona_id INTEGER;
            """))
            
            # Add persona_id to cbt_sessions
            conn.execute(text("""
                ALTER TABLE cbt_sessions 
                ADD COLUMN persona_id INTEGER;
            """))
            
            # Create indexes
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_thought_reframes_persona 
                ON thought_reframes(persona_id);
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_daily_notes_persona 
                ON daily_notes(persona_id);
            """))
            
            conn.commit()
            
        print("✅ Successfully added persona_id to CBT models!")
        print("   - thought_reframes")
        print("   - daily_notes")
        print("   - checkin_entries")
        print("   - cbt_sessions")
        print("   - Indexes created")

if __name__ == '__main__':
    migrate_persona_cbt()
```

### 8. **Testing & Documentation** 📝
**New File**: `test_mental_health_integration.py`

Tests to create:
- Mood mirroring: Verify AI tone changes based on mood
- Persona continuity: Verify CBT exercises link to correct persona
- Timeline data: Verify timeline aggregates all data sources correctly
- Crisis detection: Verify severity levels trigger appropriate responses
- Dashboard: Verify all widgets display correct data

**New File**: `MENTAL_HEALTH_COMPLETE.md`

Documentation to include:
- Feature overview
- Integration points with existing systems
- API endpoint updates
- Frontend component descriptions
- Testing procedures
- User guide for mental health features

---

## 📋 Implementation Priority

### Phase 1: Backend Integration (Days 1-2)
1. ✅ Analyze existing infrastructure (DONE)
2. ⏳ Add dynamic mood mirroring to chat service
3. ⏳ Create persona-CBT database migration
4. ⏳ Enhance crisis detection with severity levels

### Phase 2: Service & Route Updates (Days 3-4)
5. ⏳ Modify CBT services to accept persona_id
6. ⏳ Update CBT routes to pass current persona
7. ⏳ Create timeline data aggregation service
8. ⏳ Integrate crisis detection into chat flow

### Phase 3: Frontend Development (Days 5-6)
9. ⏳ Build Emotional Memory Timeline UI
10. ⏳ Enhance wellness dashboard hub
11. ⏳ Add crisis resource cards to chat UI
12. ⏳ Implement wellness reminder prompts

### Phase 4: Testing & Polish (Day 7)
13. ⏳ Create comprehensive test suite
14. ⏳ Test mood mirroring in chat
15. ⏳ Test persona continuity in CBT
16. ⏳ Test crisis detection triggers
17. ⏳ Write final documentation

---

## 🎯 Success Criteria

- [ ] AI chat tone adjusts based on user's recent mood entry
- [ ] CBT exercises remember which persona guided the session
- [ ] Emotional timeline displays mood trends and milestones
- [ ] Dashboard provides quick access to all wellness tools
- [ ] Crisis detection shows appropriate resources based on severity
- [ ] Mental health features blend seamlessly into existing app
- [ ] No breaking changes to current functionality
- [ ] Comprehensive documentation created

---

## 🔑 Key Integration Points

### 1. **Mood → Chat AI**
`MoodEntry.overall_mood` → `get_mood_adjusted_system_prompt()` → AI tone adjustment

### 2. **Persona → CBT Exercises**
`UserSettings.current_persona_id` → CBT service functions → `persona_id` in CBT models

### 3. **Timeline Data Sources**
`MoodEntry` + `WellnessAchievement` + `CBTSession` + `CheckInEntry` + `ThoughtReframe` → Timeline visualization

### 4. **Crisis Detection → Chat Flow**
User message → `detect_crisis_with_severity()` → Crisis UI + Resource display + Event logging

### 5. **Dashboard Data Sources**
`MoodEntry` (current mood) + `AchievementService` (streaks) + `WellnessGoal` (progress) + Crisis resources

---

## 📝 Notes for Implementation

1. **DO NOT REBUILD EXISTING FEATURES**: All CBT exercises, mood tracking, and wellness tools already exist and are production-ready.

2. **FOCUS ON INTEGRATION**: Connect existing systems rather than creating new ones.

3. **PERSONA CONTINUITY**: Users should feel like their chosen persona (Isabella, Maya, Alex, or custom) is guiding them through CBT exercises and wellness activities.

4. **MOOD-AWARE AI**: The AI should subtly adapt its tone based on the user's emotional state without being obvious or patronizing.

5. **CRISIS HANDLING**: Crisis detection should be gentle and supportive, not alarming or disruptive to conversation flow.

6. **PROFESSIONAL DESIGN**: All new UI components (timeline, dashboard enhancements) should match the quality and style of the existing persona system UI.

7. **MOBILE-FIRST**: Wellness features are often used on-the-go, so responsive design is critical.

8. **DATA PRIVACY**: Mental health data is sensitive. Ensure proper access controls and privacy settings for all features.

---

## 🚀 Ready to Build

**Next Step**: Start with Task #2 (Dynamic Mood Mirroring) since it's a core integration point that affects the chat experience.

All required infrastructure exists. Implementation is about **connecting the dots** rather than building from scratch. 🎯
