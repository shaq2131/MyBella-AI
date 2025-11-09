"""
Create First Admin User for MyBella
Run this script to create your first admin account
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend import create_app
from backend.database.models.models import db, User
from getpass import getpass

def create_first_admin():
    """Interactive script to create the first admin user"""
    
    app, _ = create_app()
    
    with app.app_context():
        # Check if any admin already exists
        existing_admin = User.query.filter_by(role='admin').first()
        if existing_admin:
            print("\n⚠️  Warning: An admin user already exists!")
            print(f"   Email: {existing_admin.email}")
            print(f"   Name: {existing_admin.name}")
            
            response = input("\nDo you want to create another admin? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("\n❌ Admin creation cancelled.")
                return
        
        print("\n" + "="*60)
        print("🛡️  CREATE FIRST ADMIN USER FOR MYBELLA")
        print("="*60)
        print("\nPlease provide the following information:\n")
        
        # Get admin details
        name = input("Admin Full Name: ").strip()
        if not name:
            print("❌ Error: Name is required.")
            return
        
        email = input("Admin Email: ").strip().lower()
        if not email or '@' not in email:
            print("❌ Error: Valid email is required.")
            return
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"\n❌ Error: Email '{email}' is already registered.")
            print(f"   User: {existing_user.name}")
            print(f"   Role: {existing_user.role}")
            return
        
        # Get password
        while True:
            password = getpass("Admin Password (min 8 chars): ")
            if len(password) < 8:
                print("❌ Password must be at least 8 characters long. Try again.")
                continue
            
            confirm_password = getpass("Confirm Password: ")
            if password != confirm_password:
                print("❌ Passwords do not match. Try again.")
                continue
            
            break
        
        # Get gender (optional)
        print("\nGender (optional):")
        print("1. Male")
        print("2. Female")
        print("3. Other")
        print("4. Prefer not to say")
        print("5. Skip")
        
        gender_choice = input("\nSelect option (1-5): ").strip()
        gender_map = {
            '1': 'male',
            '2': 'female',
            '3': 'other',
            '4': 'prefer_not_to_say',
            '5': None
        }
        gender = gender_map.get(gender_choice)
        
        # Create admin user
        try:
            admin = User(
                name=name,
                email=email,
                role='admin',
                gender=gender,
                active=True
            )
            admin.set_password(password)
            
            db.session.add(admin)
            db.session.commit()
            
            print("\n" + "="*60)
            print("✅ ADMIN USER CREATED SUCCESSFULLY!")
            print("="*60)
            print(f"\n📧 Email: {admin.email}")
            print(f"👤 Name: {admin.name}")
            print(f"🆔 User ID: {admin.id}")
            print(f"🛡️  Role: {admin.role}")
            print(f"\n🔗 Login at: http://localhost:5000/admin/auth/login")
            print("\n" + "="*60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error creating admin user: {str(e)}")
            return

if __name__ == '__main__':
    create_first_admin()
