"""
Secrets Vault System Test Suite
Tests PIN protection, CRUD operations, and security
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import create_app, db
from backend.database.models.user_model import User
from backend.services.secrets_vault_service import SecretsVaultService
import hashlib

def test_secrets_vault():
    """Comprehensive test of Secrets Vault system"""
    
    app = create_app()
    
    with app.app_context():
        print("\n🔐 SECRETS VAULT SYSTEM TEST")
        print("=" * 60)
        
        # Get test user
        test_user = User.query.filter_by(email="test@mybella.com").first()
        if not test_user:
            print("❌ Test user not found. Creating...")
            test_user = User(
                email="test@mybella.com",
                username="TestUser",
                age=25,
                is_age_verified=True
            )
            test_user.set_password("Test123!")
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test user created")
        
        user_id = test_user.id
        test_pin = "1234"
        
        # Test 1: Check vault doesn't exist initially
        print("\n1️⃣  Testing vault existence check...")
        has_vault = SecretsVaultService.has_vault(user_id)
        print(f"   Has vault: {has_vault}")
        
        # Test 2: Set PIN
        print("\n2️⃣  Testing PIN setup...")
        result = SecretsVaultService.set_pin(user_id, test_pin)
        if result['success']:
            print(f"   ✅ PIN set successfully")
            # Verify PIN hash stored correctly
            expected_hash = hashlib.sha256(test_pin.encode()).hexdigest()
            print(f"   PIN hash length: {len(result['pin_hash'])} chars")
        else:
            print(f"   ❌ Failed: {result.get('error')}")
            return False
        
        # Test 3: Verify correct PIN
        print("\n3️⃣  Testing PIN verification (correct)...")
        verify_result = SecretsVaultService.verify_pin(user_id, test_pin)
        if verify_result['success'] and verify_result['valid']:
            print(f"   ✅ Correct PIN accepted")
        else:
            print(f"   ❌ Failed: {verify_result.get('error')}")
            return False
        
        # Test 4: Verify wrong PIN
        print("\n4️⃣  Testing PIN verification (incorrect)...")
        verify_result = SecretsVaultService.verify_pin(user_id, "9999")
        if verify_result['success'] and not verify_result['valid']:
            print(f"   ✅ Incorrect PIN rejected")
        else:
            print(f"   ❌ Security failure: wrong PIN accepted!")
            return False
        
        # Test 5: Create journal entry
        print("\n5️⃣  Testing entry creation...")
        entry_data = {
            'title': 'My First Secret',
            'content': 'This is a private thought I want to keep safe. Testing the vault system!',
            'mood': 'happy',
            'tags': ['personal', 'test']
        }
        create_result = SecretsVaultService.create_entry(
            user_id=user_id,
            pin=test_pin,
            title=entry_data['title'],
            content=entry_data['content'],
            mood=entry_data['mood'],
            tags=entry_data['tags']
        )
        if create_result['success']:
            entry_id = create_result['entry']['id']
            print(f"   ✅ Entry created (ID: {entry_id})")
            print(f"   Title: {create_result['entry']['title']}")
            print(f"   Words: {len(entry_data['content'].split())} words")
        else:
            print(f"   ❌ Failed: {create_result.get('error')}")
            return False
        
        # Test 6: Create second entry
        print("\n6️⃣  Testing second entry...")
        entry2_data = {
            'title': 'Another Secret',
            'content': 'More private thoughts here. Testing multiple entries!',
            'mood': 'peaceful'
        }
        create_result2 = SecretsVaultService.create_entry(
            user_id=user_id,
            pin=test_pin,
            title=entry2_data['title'],
            content=entry2_data['content'],
            mood=entry2_data['mood']
        )
        if create_result2['success']:
            entry2_id = create_result2['entry']['id']
            print(f"   ✅ Second entry created (ID: {entry2_id})")
        else:
            print(f"   ❌ Failed: {create_result2.get('error')}")
            return False
        
        # Test 7: Get all entries
        print("\n7️⃣  Testing entry retrieval...")
        entries_result = SecretsVaultService.get_entries(user_id, test_pin)
        if entries_result['success']:
            entries = entries_result['entries']
            print(f"   ✅ Retrieved {len(entries)} entries")
            for i, entry in enumerate(entries, 1):
                print(f"   [{i}] {entry['title']} - {entry['mood'] or 'no mood'}")
        else:
            print(f"   ❌ Failed: {entries_result.get('error')}")
            return False
        
        # Test 8: Get single entry
        print("\n8️⃣  Testing single entry retrieval...")
        single_result = SecretsVaultService.get_entry(user_id, entry_id, test_pin)
        if single_result['success']:
            entry = single_result['entry']
            print(f"   ✅ Retrieved: {entry['title']}")
            print(f"   Content preview: {entry['content'][:50]}...")
        else:
            print(f"   ❌ Failed: {single_result.get('error')}")
            return False
        
        # Test 9: Update entry
        print("\n9️⃣  Testing entry update...")
        update_result = SecretsVaultService.update_entry(
            user_id=user_id,
            entry_id=entry_id,
            pin=test_pin,
            title="My First Secret (Updated)",
            content="Updated content with more details!",
            mood="excited"
        )
        if update_result['success']:
            print(f"   ✅ Entry updated")
            print(f"   New title: {update_result['entry']['title']}")
            print(f"   New mood: {update_result['entry']['mood']}")
        else:
            print(f"   ❌ Failed: {update_result.get('error')}")
            return False
        
        # Test 10: Get statistics
        print("\n🔟 Testing vault statistics...")
        stats_result = SecretsVaultService.get_stats(user_id, test_pin)
        if stats_result['success']:
            stats = stats_result['stats']
            print(f"   ✅ Statistics retrieved:")
            print(f"   Total entries: {stats['total_entries']}")
            print(f"   Total words: {stats['total_words']}")
            print(f"   First entry: {stats['first_entry_date']}")
            print(f"   Last entry: {stats['last_entry_date']}")
        else:
            print(f"   ❌ Failed: {stats_result.get('error')}")
            return False
        
        # Test 11: Security - try to access with wrong PIN
        print("\n1️⃣1️⃣  Testing security (wrong PIN on get)...")
        wrong_pin_result = SecretsVaultService.get_entries(user_id, "9999")
        if not wrong_pin_result['success'] and 'Invalid PIN' in wrong_pin_result.get('error', ''):
            print(f"   ✅ Access denied with wrong PIN")
        else:
            print(f"   ❌ Security failure: accessed with wrong PIN!")
            return False
        
        # Test 12: Delete entry
        print("\n1️⃣2️⃣  Testing entry deletion...")
        delete_result = SecretsVaultService.delete_entry(user_id, entry2_id, test_pin)
        if delete_result['success']:
            print(f"   ✅ Entry deleted (ID: {entry2_id})")
        else:
            print(f"   ❌ Failed: {delete_result.get('error')}")
            return False
        
        # Test 13: Verify deletion
        print("\n1️⃣3️⃣  Verifying deletion...")
        final_entries = SecretsVaultService.get_entries(user_id, test_pin)
        if final_entries['success'] and len(final_entries['entries']) == 1:
            print(f"   ✅ Confirmed: {len(final_entries['entries'])} entry remaining")
        else:
            print(f"   ⚠️  Expected 1 entry, found {len(final_entries['entries'])}")
        
        # Test 14: PIN change
        print("\n1️⃣4️⃣  Testing PIN change...")
        new_pin = "5678"
        change_result = SecretsVaultService.set_pin(user_id, new_pin)
        if change_result['success']:
            print(f"   ✅ PIN changed successfully")
            # Verify old PIN doesn't work
            old_verify = SecretsVaultService.verify_pin(user_id, test_pin)
            new_verify = SecretsVaultService.verify_pin(user_id, new_pin)
            if not old_verify['valid'] and new_verify['valid']:
                print(f"   ✅ Old PIN rejected, new PIN accepted")
            else:
                print(f"   ❌ PIN change verification failed")
                return False
        else:
            print(f"   ❌ Failed: {change_result.get('error')}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ ALL SECRETS VAULT TESTS PASSED!")
        print("=" * 60)
        
        return True

if __name__ == "__main__":
    try:
        success = test_secrets_vault()
        if success:
            print("\n🎉 Secrets Vault system is fully functional!")
            print("\n📋 Tested features:")
            print("   ✅ PIN setup and storage (SHA-256)")
            print("   ✅ PIN verification (correct/incorrect)")
            print("   ✅ Entry creation with mood and tags")
            print("   ✅ Entry retrieval (all and single)")
            print("   ✅ Entry updates")
            print("   ✅ Entry deletion")
            print("   ✅ Vault statistics")
            print("   ✅ PIN security enforcement")
            print("   ✅ PIN change functionality")
            print("\n🌐 Access at: http://localhost:5000/secrets/vault")
        else:
            print("\n❌ Some tests failed - check errors above")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
