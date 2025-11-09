"""
Migration: Add Secrets Vault Table
Creates the secret_vault_entries table for PIN-protected journal feature
"""

from backend import create_app, db
from backend.database.models.wellness_models import SecretVaultEntry

def run_migration():
    """Add secret_vault_entries table"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔐 Adding Secrets Vault table...")
            
            # Create the table
            db.create_all()
            
            print("✅ secret_vault_entries table created successfully!")
            print("📊 Table structure:")
            print("  - id (Primary Key)")
            print("  - user_id (Foreign Key → users)")
            print("  - title (String)")
            print("  - content (Text)")
            print("  - pin_hash (String - SHA-256)")
            print("  - tags (JSON)")
            print("  - mood (String)")
            print("  - is_encrypted (Boolean)")
            print("  - created_at (DateTime)")
            print("  - updated_at (DateTime)")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            return False

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("\n🎉 Secrets Vault is ready to use!")
        print("   Visit: /secrets/vault")
    else:
        print("\n⚠️  Please fix errors and run again")
