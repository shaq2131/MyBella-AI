"""
Test Persona-CBT Integration
Tests that CBT exercises maintain persona continuity across sessions.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend import create_app
from backend.database.models.models import db, User, PersonaProfile
from backend.database.models.wellness_models import (
    ThoughtReframe, DailyNote, CheckInEntry, CBTSession, EmotionMatch
)
from datetime import date, datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_thought_reframe_persona():
    """Test ThoughtReframe with persona_id"""
    logger.info("🧪 Testing ThoughtReframe persona integration...")
    
    app, _ = create_app()
    with app.app_context():
        # Get test user and persona
        user = User.query.first()
        persona = PersonaProfile.query.first()
        
        if not user or not persona:
            logger.error("   ❌ No test user or persona found")
            return False
        
        # Create thought reframe with persona
        reframe = ThoughtReframe(
            user_id=user.id,
            persona_id=persona.id,
            negative_thought="I always fail at everything",
            cognitive_distortion="overgeneralization",
            user_reframe="Sometimes I make mistakes, but I also succeed often",
            quality_score=8,
            completed=True
        )
        
        db.session.add(reframe)
        db.session.commit()
        
        # Verify relationship works
        saved_reframe = ThoughtReframe.query.filter_by(id=reframe.id).first()
        if saved_reframe and saved_reframe.persona_id == persona.id:
            logger.info(f"   ✅ ThoughtReframe created with persona: {saved_reframe.persona.name if saved_reframe.persona else 'None'}")
            
            # Test relationship access
            if saved_reframe.persona and saved_reframe.persona.name == persona.name:
                logger.info(f"   ✅ Persona relationship accessible: {saved_reframe.persona.name}")
                return True
            else:
                logger.error("   ❌ Persona relationship not accessible")
                return False
        else:
            logger.error("   ❌ Failed to save ThoughtReframe with persona")
            return False


def test_daily_note_persona():
    """Test DailyNote with persona_id"""
    logger.info("🧪 Testing DailyNote persona integration...")
    
    app, _ = create_app()
    with app.app_context():
        user = User.query.first()
        persona = PersonaProfile.query.first()
        
        if not user or not persona:
            logger.error("   ❌ No test user or persona found")
            return False
        
        note = DailyNote(
            user_id=user.id,
            persona_id=persona.id,
            note_type="reflection",
            title="Today's Reflection",
            content="I felt productive today and accomplished my goals.",
            note_date=date.today()
        )
        
        db.session.add(note)
        db.session.commit()
        
        saved_note = DailyNote.query.filter_by(id=note.id).first()
        if saved_note and saved_note.persona_id == persona.id:
            logger.info(f"   ✅ DailyNote created with persona: {saved_note.persona.name if saved_note.persona else 'None'}")
            return True
        else:
            logger.error("   ❌ Failed to save DailyNote with persona")
            return False


def test_checkin_entry_persona():
    """Test CheckInEntry with persona_id"""
    logger.info("🧪 Testing CheckInEntry persona integration...")
    
    app, _ = create_app()
    with app.app_context():
        user = User.query.first()
        persona = PersonaProfile.query.first()
        
        if not user or not persona:
            logger.error("   ❌ No test user or persona found")
            return False
        
        from backend.database.models.wellness_models import MoodScale
        
        checkin = CheckInEntry(
            user_id=user.id,
            persona_id=persona.id,
            checkin_type="morning",
            checkin_date=date.today(),
            morning_mood=MoodScale.GOOD,
            morning_intention="Focus on one task at a time",
            ai_message=f"Good morning! {persona.name} here. Let's make today great!"
        )
        
        db.session.add(checkin)
        db.session.commit()
        
        saved_checkin = CheckInEntry.query.filter_by(id=checkin.id).first()
        if saved_checkin and saved_checkin.persona_id == persona.id:
            logger.info(f"   ✅ CheckInEntry created with persona: {saved_checkin.persona.name if saved_checkin.persona else 'None'}")
            return True
        else:
            logger.error("   ❌ Failed to save CheckInEntry with persona")
            return False


def test_cbt_session_persona():
    """Test CBTSession with persona_id"""
    logger.info("🧪 Testing CBTSession persona integration...")
    
    app, _ = create_app()
    with app.app_context():
        user = User.query.first()
        persona = PersonaProfile.query.first()
        
        if not user or not persona:
            logger.error("   ❌ No test user or persona found")
            return False
        
        from backend.database.models.wellness_models import MoodScale
        
        session = CBTSession(
            user_id=user.id,
            persona_id=persona.id,
            session_type="thought_challenging",
            trigger_event="Stressful work meeting",
            initial_mood=MoodScale.SOMEWHAT_LOW,
            final_mood=MoodScale.AVERAGE,
            automatic_thoughts="I'm going to fail this project",
            balanced_thought="I have skills and support to succeed",
            completed=True
        )
        
        db.session.add(session)
        db.session.commit()
        
        saved_session = CBTSession.query.filter_by(id=session.id).first()
        if saved_session and saved_session.persona_id == persona.id:
            logger.info(f"   ✅ CBTSession created with persona: {saved_session.persona_profile.name if saved_session.persona_profile else 'None'}")
            return True
        else:
            logger.error("   ❌ Failed to save CBTSession with persona")
            return False


def test_emotion_match_persona():
    """Test EmotionMatch with persona_id"""
    logger.info("🧪 Testing EmotionMatch persona integration...")
    
    app, _ = create_app()
    with app.app_context():
        user = User.query.first()
        persona = PersonaProfile.query.first()
        
        if not user or not persona:
            logger.error("   ❌ No test user or persona found")
            return False
        
        game = EmotionMatch(
            user_id=user.id,
            persona_id=persona.id,
            game_type="emotion_coping",
            difficulty_level=1,
            total_pairs=8,
            matched_pairs=8,
            time_seconds=120,
            score=100,
            completed=True
        )
        
        db.session.add(game)
        db.session.commit()
        
        saved_game = EmotionMatch.query.filter_by(id=game.id).first()
        if saved_game and saved_game.persona_id == persona.id:
            logger.info(f"   ✅ EmotionMatch created with persona: {saved_game.persona.name if saved_game.persona else 'None'}")
            return True
        else:
            logger.error("   ❌ Failed to save EmotionMatch with persona")
            return False


def test_persona_continuity():
    """Test that persona continuity works across multiple CBT activities"""
    logger.info("🧪 Testing persona continuity across CBT activities...")
    
    app, _ = create_app()
    with app.app_context():
        user = User.query.first()
        persona = PersonaProfile.query.first()
        
        if not user or not persona:
            logger.error("   ❌ No test user or persona found")
            return False
        
        # Simulate user doing multiple CBT activities with same persona
        activities_created = []
        
        # Morning check-in
        from backend.database.models.wellness_models import MoodScale
        checkin = CheckInEntry(
            user_id=user.id,
            persona_id=persona.id,
            checkin_type="morning",
            checkin_date=date.today(),
            morning_mood=MoodScale.AVERAGE
        )
        db.session.add(checkin)
        activities_created.append("checkin")
        
        # Thought reframe during day
        reframe = ThoughtReframe(
            user_id=user.id,
            persona_id=persona.id,
            negative_thought="I'm not good enough",
            user_reframe="I'm learning and growing every day",
            completed=True
        )
        db.session.add(reframe)
        activities_created.append("reframe")
        
        # Evening note
        note = DailyNote(
            user_id=user.id,
            persona_id=persona.id,
            note_type="reflection",
            content="Reflected on my day with mindfulness",
            note_date=date.today()
        )
        db.session.add(note)
        activities_created.append("note")
        
        db.session.commit()
        
        # Verify all activities have same persona
        saved_checkin = CheckInEntry.query.filter_by(user_id=user.id).order_by(CheckInEntry.id.desc()).first()
        saved_reframe = ThoughtReframe.query.filter_by(user_id=user.id).order_by(ThoughtReframe.id.desc()).first()
        saved_note = DailyNote.query.filter_by(user_id=user.id).order_by(DailyNote.id.desc()).first()
        
        all_same_persona = (
            saved_checkin and saved_checkin.persona_id == persona.id and
            saved_reframe and saved_reframe.persona_id == persona.id and
            saved_note and saved_note.persona_id == persona.id
        )
        
        if all_same_persona:
            logger.info(f"   ✅ Persona continuity maintained across {len(activities_created)} activities: {', '.join(activities_created)}")
            logger.info(f"   ✅ All activities linked to persona: {persona.name}")
            return True
        else:
            logger.error("   ❌ Persona continuity broken across activities")
            return False


def test_query_by_persona():
    """Test querying CBT activities by persona"""
    logger.info("🧪 Testing query CBT activities by persona...")
    
    app, _ = create_app()
    with app.app_context():
        persona = PersonaProfile.query.first()
        
        if not persona:
            logger.error("   ❌ No persona found")
            return False
        
        # Query all activities for this persona
        reframes = ThoughtReframe.query.filter_by(persona_id=persona.id).all()
        notes = DailyNote.query.filter_by(persona_id=persona.id).all()
        checkins = CheckInEntry.query.filter_by(persona_id=persona.id).all()
        sessions = CBTSession.query.filter_by(persona_id=persona.id).all()
        games = EmotionMatch.query.filter_by(persona_id=persona.id).all()
        
        total_activities = len(reframes) + len(notes) + len(checkins) + len(sessions) + len(games)
        
        logger.info(f"   ✅ Found {total_activities} activities for persona '{persona.name}':")
        logger.info(f"      - {len(reframes)} thought reframes")
        logger.info(f"      - {len(notes)} daily notes")
        logger.info(f"      - {len(checkins)} check-ins")
        logger.info(f"      - {len(sessions)} CBT sessions")
        logger.info(f"      - {len(games)} emotion match games")
        
        return True


def run_all_tests():
    """Run all persona-CBT integration tests"""
    logger.info("="*60)
    logger.info("🚀 PERSONA-CBT INTEGRATION TESTS")
    logger.info("="*60)
    logger.info("Testing persona continuity in CBT wellness activities\n")
    
    tests = [
        ("ThoughtReframe Persona", test_thought_reframe_persona),
        ("DailyNote Persona", test_daily_note_persona),
        ("CheckInEntry Persona", test_checkin_entry_persona),
        ("CBTSession Persona", test_cbt_session_persona),
        ("EmotionMatch Persona", test_emotion_match_persona),
        ("Persona Continuity", test_persona_continuity),
        ("Query By Persona", test_query_by_persona),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            logger.info(f"\n▶️  Running: {test_name}")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"   ❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("📊 TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    logger.info("="*60)
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("="*60)
    
    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED!")
        logger.info("✨ Persona-CBT integration working perfectly!")
    else:
        logger.warning(f"\n⚠️  {total - passed} test(s) failed")
    
    return passed == total


if __name__ == '__main__':
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
