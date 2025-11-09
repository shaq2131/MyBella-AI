"""
Migration: Add Professional SaaS Features
- Onboarding Quiz for first-run personalization
- User Disclaimer Acceptance tracking
- Crisis Resources by region
- User Memory Controls
- Content Moderation Logging
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend import create_app
from backend.database.models.models import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_crisis_resources():
    """Seed initial crisis resources"""
    from backend.database.models.onboarding_models import CrisisResource
    
    logger.info("🌍 Seeding crisis resources...")
    
    resources = [
        # United States
        {
            'country_code': 'US',
            'country_name': 'United States',
            'resource_type': 'suicide',
            'organization_name': '988 Suicide & Crisis Lifeline',
            'phone_number': '988',
            'sms_number': '988',
            'website_url': 'https://988lifeline.org',
            'chat_url': 'https://988lifeline.org/chat',
            'available_24_7': True,
            'languages': '["en", "es"]',
            'priority': 1
        },
        {
            'country_code': 'US',
            'country_name': 'United States',
            'resource_type': 'mental_health',
            'organization_name': 'SAMHSA National Helpline',
            'phone_number': '1-800-662-4357',
            'website_url': 'https://www.samhsa.gov/find-help/national-helpline',
            'available_24_7': True,
            'languages': '["en", "es"]',
            'priority': 2
        },
        {
            'country_code': 'US',
            'country_name': 'United States',
            'resource_type': 'mental_health',
            'organization_name': 'Crisis Text Line',
            'sms_number': '741741',
            'website_url': 'https://www.crisistextline.org',
            'available_24_7': True,
            'languages': '["en"]',
            'priority': 3
        },
        # United Kingdom
        {
            'country_code': 'GB',
            'country_name': 'United Kingdom',
            'resource_type': 'suicide',
            'organization_name': 'Samaritans',
            'phone_number': '116 123',
            'website_url': 'https://www.samaritans.org',
            'available_24_7': True,
            'languages': '["en"]',
            'priority': 1
        },
        # Canada
        {
            'country_code': 'CA',
            'country_name': 'Canada',
            'resource_type': 'suicide',
            'organization_name': 'Talk Suicide Canada',
            'phone_number': '1-833-456-4566',
            'sms_number': '45645',
            'website_url': 'https://talksuicide.ca',
            'available_24_7': True,
            'languages': '["en", "fr"]',
            'priority': 1
        },
        # Australia
        {
            'country_code': 'AU',
            'country_name': 'Australia',
            'resource_type': 'suicide',
            'organization_name': 'Lifeline',
            'phone_number': '13 11 14',
            'website_url': 'https://www.lifeline.org.au',
            'chat_url': 'https://www.lifeline.org.au/crisis-chat',
            'available_24_7': True,
            'languages': '["en"]',
            'priority': 1
        },
        # International
        {
            'country_code': 'XX',
            'country_name': 'International',
            'resource_type': 'suicide',
            'organization_name': 'Befrienders Worldwide',
            'website_url': 'https://www.befrienders.org',
            'available_24_7': False,
            'description': 'Find a helpline in your country',
            'priority': 10
        }
    ]
    
    added_count = 0
    for resource_data in resources:
        # Check if already exists
        existing = CrisisResource.query.filter_by(
            country_code=resource_data['country_code'],
            resource_type=resource_data['resource_type'],
            organization_name=resource_data['organization_name']
        ).first()
        
        if not existing:
            resource = CrisisResource(**resource_data)
            db.session.add(resource)
            added_count += 1
    
    db.session.commit()
    logger.info(f"   ✅ Added {added_count} crisis resources")


def run_migration():
    """Run the complete migration"""
    logger.info("="*60)
    logger.info("🚀 PROFESSIONAL SAAS FEATURES MIGRATION")
    logger.info("="*60)
    logger.info("Adding onboarding, safety, and trust features\n")
    
    app, _ = create_app()
    with app.app_context():
        try:
            # Create all tables from onboarding_models
            logger.info("📊 Creating database tables...")
            db.create_all()
            logger.info("   ✅ Tables created successfully")
            
            # Seed crisis resources
            seed_crisis_resources()
            
            logger.info("\n" + "="*60)
            logger.info("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            logger.info("="*60)
            logger.info("\n✨ New Features Available:")
            logger.info("   1. ✅ Onboarding Quiz - 60s personalization flow")
            logger.info("   2. ✅ Disclaimer Tracking - Legal compliance")
            logger.info("   3. ✅ Crisis Resources - Region-aware support")
            logger.info("   4. ✅ Memory Controls - User privacy & GDPR")
            logger.info("   5. ✅ Content Moderation - Safety logging")
            
            logger.info("\n📋 Next Steps:")
            logger.info("   1. Create onboarding quiz UI")
            logger.info("   2. Build memory management page")
            logger.info("   3. Implement crisis detection flow")
            logger.info("   4. Add content moderation filters")
            logger.info("   5. Set up analytics events")
            
            return True
            
        except Exception as e:
            logger.error(f"\n❌ MIGRATION FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    try:
        success = run_migration()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"\n❌ MIGRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
