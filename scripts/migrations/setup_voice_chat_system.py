"""
Setup Voice Chat System Migration
- Ensures all users have voice minutes allocated
- Updates subscription defaults for voice chat
- Sets up free tier: 100 minutes/month
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend import create_app
from backend.database.models.models import db, User, UserSubscription
from datetime import datetime, timedelta

def setup_voice_chat_system():
    """Setup voice chat system with default allocations"""
    
    app, socketio = create_app()
    
    with app.app_context():
        print("\n=== Voice Chat System Setup ===\n")
        
        # Get all users
        users = User.query.all()
        print(f"Found {len(users)} users in database")
        
        updated_count = 0
        created_count = 0
        
        for user in users:
            # Check if user has subscription
            if not user.subscription:
                # Create new subscription with voice minutes
                subscription = UserSubscription(
                    user_id=user.id,
                    subscription_type='free',
                    subscription_status='active',
                    total_minutes=100,  # 100 minutes free per month
                    used_minutes=0.0,
                    remaining_minutes=100.0
                )
                db.session.add(subscription)
                created_count += 1
                print(f"✓ Created subscription for {user.name} ({user.email}): 100 voice minutes")
            else:
                # Update existing subscription
                sub = user.subscription
                
                # Set voice minutes based on subscription type
                if sub.subscription_type == 'free':
                    sub.total_minutes = 100  # 100 minutes/month for free users
                elif sub.subscription_type == 'basic':
                    sub.total_minutes = 500  # 500 minutes/month for basic
                elif sub.subscription_type == 'premium':
                    sub.total_minutes = 999999  # Unlimited for premium (effectively)
                else:
                    sub.total_minutes = 100  # Default to free tier
                
                # Reset used minutes if this is a new month
                if not hasattr(sub, 'last_reset') or sub.updated_at.month != datetime.utcnow().month:
                    sub.used_minutes = 0.0
                
                sub.remaining_minutes = sub.total_minutes - sub.used_minutes
                updated_count += 1
                print(f"✓ Updated {user.name}: {sub.total_minutes} total minutes, {sub.remaining_minutes:.1f} remaining")
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"\n✅ Success!")
            print(f"   - Created {created_count} new subscriptions")
            print(f"   - Updated {updated_count} existing subscriptions")
            print(f"\n📊 Voice Chat System Ready!")
            print(f"   - Free users: 100 minutes/month")
            print(f"   - Basic users: 500 minutes/month")
            print(f"   - Premium users: Unlimited")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error: {e}")
            return False
        
        return True

if __name__ == '__main__':
    setup_voice_chat_system()
