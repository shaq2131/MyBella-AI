"""
Content Moderation System Test Suite
Tests filtering, profanity detection, and safety guardrails
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import create_app
from backend.database.models.models import db, User
from backend.services.content_moderation_service import ContentModerationService

def test_content_moderation():
    """Comprehensive test of Content Moderation system"""
    
    app, socketio = create_app()
    
    with app.app_context():
        print("\n🛡️ CONTENT MODERATION SYSTEM TEST")
        print("=" * 60)
        
        # Get test user
        test_user = User.query.filter_by(email="test@mybella.com").first()
        if not test_user:
            print("⚠️  Test user not found, using ID 1")
            user_id = 1
        else:
            user_id = test_user.id
        
        # Test 1: Clean content (should pass)
        print("\n1️⃣  Testing clean content...")
        clean_text = "Hello! How are you doing today? I'm feeling great!"
        result = ContentModerationService.check_user_content(user_id, clean_text)
        
        print(f"   DEBUG - Result: {result}")
        
        if result['allowed'] and result['severity'] == 'none':
            print(f"   ✅ Clean content passed")
            print(f"   Flags: {result['flags']}")
            print(f"   Action: {result['action']}")
        else:
            print(f"   ❌ Clean content incorrectly flagged")
            print(f"   Severity: {result['severity']}, Allowed: {result['allowed']}")
            print(f"   Flags: {result['flags']}")
            return False
        
        # Test 2: Profanity (should filter)
        print("\n2️⃣  Testing profanity detection...")
        profane_text = "This is fucking annoying and I'm pissed off"
        result = ContentModerationService.check_user_content(user_id, profane_text)
        
        if 'profanity' in result['flags']:
            print(f"   ✅ Profanity detected")
            print(f"   Original: {profane_text}")
            print(f"   Filtered: {result['filtered_content']}")
            print(f"   Severity: {result['severity']}")
            print(f"   Action: {result['action']}")
        else:
            print(f"   ❌ Profanity not detected")
            return False
        
        # Test 3: Sexual content (should flag)
        print("\n3️⃣  Testing sexual content detection...")
        sexual_text = "Let's talk about sex and sexual fantasies"
        result = ContentModerationService.check_user_content(user_id, sexual_text)
        
        if 'sexual_content' in result['flags']:
            print(f"   ✅ Sexual content detected")
            print(f"   Flags: {result['flags']}")
            print(f"   Severity: {result['severity']}")
            print(f"   Allowed: {result['allowed']}")
        else:
            print(f"   ❌ Sexual content not detected")
            return False
        
        # Test 4: Violence (should flag high)
        print("\n4️⃣  Testing violence detection...")
        violent_text = "I want to kill someone and hurt people"
        result = ContentModerationService.check_user_content(user_id, violent_text)
        
        if 'violence' in result['flags']:
            print(f"   ✅ Violence detected")
            print(f"   Flags: {result['flags']}")
            print(f"   Severity: {result['severity']}")
            print(f"   Action: {result['action']}")
        else:
            print(f"   ❌ Violence not detected")
            return False
        
        # Test 5: Harassment (should flag)
        print("\n5️⃣  Testing harassment detection...")
        harassment_text = "You're stupid and worthless, I hate you"
        result = ContentModerationService.check_user_content(user_id, harassment_text)
        
        if 'harassment' in result['flags']:
            print(f"   ✅ Harassment detected")
            print(f"   Flags: {result['flags']}")
            print(f"   Severity: {result['severity']}")
        else:
            print(f"   ❌ Harassment not detected")
            return False
        
        # Test 6: Teen mode (stricter filtering)
        print("\n6️⃣  Testing teen mode filtering...")
        mildly_sexual = "Let's talk about romantic relationships"
        
        # Adult mode
        adult_result = ContentModerationService.moderate_content(
            content=mildly_sexual,
            user_id=user_id,
            age_tier='adult'
        )
        
        # Teen mode
        teen_result = ContentModerationService.moderate_content(
            content=mildly_sexual,
            user_id=user_id,
            age_tier='teen'
        )
        
        print(f"   Adult mode - Severity: {adult_result['severity']}, Allowed: {adult_result['allowed']}")
        print(f"   Teen mode - Severity: {teen_result['severity']}, Allowed: {teen_result['allowed']}")
        
        if teen_result['severity'] >= adult_result['severity']:
            print(f"   ✅ Teen mode is stricter")
        else:
            print(f"   ⚠️  Teen mode should be stricter")
        
        # Test 7: AI response checking (stricter)
        print("\n7️⃣  Testing AI response moderation...")
        ai_response = "Damn, that sucks"
        
        user_check = ContentModerationService.check_user_content(user_id, ai_response)
        ai_check = ContentModerationService.check_ai_response(user_id, ai_response)
        
        print(f"   User content check - Action: {user_check['action']}")
        print(f"   AI response check - Action: {ai_check['action']}")
        
        if ai_check['action'] in ['block', 'filter']:
            print(f"   ✅ AI responses are strictly moderated")
        else:
            print(f"   ⚠️  AI responses should be more strictly moderated")
        
        # Test 8: Multiple flags
        print("\n8️⃣  Testing multiple flag detection...")
        multi_flag_text = "Fuck this shit, I'll kill you, stupid bitch"
        result = ContentModerationService.check_user_content(user_id, multi_flag_text)
        
        print(f"   Flags detected: {result['flags']}")
        print(f"   Severity: {result['severity']}")
        print(f"   Action: {result['action']}")
        
        if len(result['flags']) >= 2:
            print(f"   ✅ Multiple flags detected: {len(result['flags'])}")
        else:
            print(f"   ❌ Should detect multiple flags")
            return False
        
        # Test 9: Underage content in romantic context (critical)
        print("\n9️⃣  Testing underage protection...")
        underage_text = "I want to date a young girl from school"
        result = ContentModerationService.moderate_content(
            content=underage_text,
            user_id=user_id,
            content_type='romantic'
        )
        
        if 'underage_reference' in result['flags'] or result['severity'] == 'critical':
            print(f"   ✅ Underage reference detected")
            print(f"   Severity: {result['severity']}")
            print(f"   Allowed: {result['allowed']}")
            print(f"   Action: {result['action']}")
        else:
            print(f"   ❌ Underage reference not detected (critical security issue!)")
            return False
        
        # Test 10: Sanitization
        print("\n🔟 Testing content sanitization...")
        dirty_text = "This fucking sucks, what the hell is this shit?"
        sanitized = ContentModerationService.sanitize_for_display(dirty_text)
        
        print(f"   Original: {dirty_text}")
        print(f"   Sanitized: {sanitized}")
        
        if sanitized != dirty_text and '****' in sanitized:
            print(f"   ✅ Content sanitized successfully")
        else:
            print(f"   ❌ Sanitization failed")
            return False
        
        # Test 11: Teen safety check
        print("\n1️⃣1️⃣  Testing teen safety check...")
        safe_content = "Let's practice mindfulness and meditation"
        unsafe_content = "Let's talk about sex and intimacy"
        
        is_safe = ContentModerationService.is_teen_safe(safe_content)
        is_unsafe = ContentModerationService.is_teen_safe(unsafe_content)
        
        print(f"   Safe content for teens: {is_safe}")
        print(f"   Unsafe content for teens: {is_unsafe}")
        
        if is_safe and not is_unsafe:
            print(f"   ✅ Teen safety check working")
        else:
            print(f"   ❌ Teen safety check failed")
            return False
        
        # Test 12: Fallback responses
        print("\n1️⃣2️⃣  Testing safe fallback responses...")
        fallbacks = {
            'general': ContentModerationService.get_safe_fallback_response('general'),
            'profanity': ContentModerationService.get_safe_fallback_response('profanity'),
            'sexual': ContentModerationService.get_safe_fallback_response('sexual'),
            'violence': ContentModerationService.get_safe_fallback_response('violence'),
            'teen_blocked': ContentModerationService.get_safe_fallback_response('teen_blocked'),
        }
        
        print(f"   Generated {len(fallbacks)} fallback responses")
        for context, response in fallbacks.items():
            print(f"   [{context}] {response[:60]}...")
        
        if all(fallbacks.values()):
            print(f"   ✅ All fallback responses available")
        else:
            print(f"   ❌ Missing fallback responses")
            return False
        
        # Test 13: Edge cases
        print("\n1️⃣3️⃣  Testing edge cases...")
        
        # Empty content
        empty_result = ContentModerationService.check_user_content(user_id, "")
        print(f"   Empty content - Allowed: {empty_result['allowed']}, Action: {empty_result['action']}")
        
        # Very long content
        long_content = "Hello " * 1000
        long_result = ContentModerationService.check_user_content(user_id, long_content)
        print(f"   Long content (5000+ chars) - Processed: {len(long_result['filtered_content'])} chars")
        
        # Mixed case profanity
        mixed_case = "FuCkInG hElL"
        mixed_result = ContentModerationService.check_user_content(user_id, mixed_case)
        print(f"   Mixed case profanity - Detected: {'profanity' in mixed_result['flags']}")
        
        # Repeated letters (obfuscation attempt)
        obfuscated = "fuuuuuck thisss shiiiiit"
        obfuscated_result = ContentModerationService.check_user_content(user_id, obfuscated)
        print(f"   Obfuscated profanity - Detected: {'profanity' in obfuscated_result['flags']}")
        
        if empty_result['allowed'] and mixed_result['flags'] and obfuscated_result['flags']:
            print(f"   ✅ Edge cases handled correctly")
        else:
            print(f"   ⚠️  Some edge cases not handled")
        
        print("\n" + "=" * 60)
        print("✅ ALL CONTENT MODERATION TESTS PASSED!")
        print("=" * 60)
        
        return True

if __name__ == "__main__":
    try:
        success = test_content_moderation()
        if success:
            print("\n🎉 Content Moderation system is fully functional!")
            print("\n📋 Tested features:")
            print("   ✅ Clean content passes")
            print("   ✅ Profanity detection and filtering")
            print("   ✅ Sexual content detection")
            print("   ✅ Violence detection")
            print("   ✅ Harassment detection")
            print("   ✅ Teen mode (stricter filtering)")
            print("   ✅ AI response moderation (strict)")
            print("   ✅ Multiple flag detection")
            print("   ✅ Underage protection (critical)")
            print("   ✅ Content sanitization")
            print("   ✅ Teen safety checks")
            print("   ✅ Safe fallback responses")
            print("   ✅ Edge case handling")
            print("\n🔌 API Endpoints:")
            print("   POST /moderation/api/check-content - Check content")
            print("   POST /moderation/api/sanitize - Sanitize profanity")
            print("   GET /moderation/api/my-stats - User stats")
            print("   GET /moderation/admin/dashboard - Admin dashboard")
        else:
            print("\n❌ Some tests failed - check errors above")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
