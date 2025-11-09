# Seeds Directory

This directory contains database seeding scripts for populating initial data.

## Usage

Place your database seeding scripts here. Example structure:

```
seeds/
├── __init__.py
├── seed_personas.py      # Initial persona data
├── seed_users.py         # Test user accounts
└── seed_data.py          # General application data
```

## Creating Seed Scripts

Each seed script should:
1. Import necessary models from `backend.database.models.models`
2. Create sample data for testing/development
3. Handle existing data gracefully (check before creating)
4. Include rollback/cleanup functionality

Example seed script:
```python
from backend.database.models.models import PersonaProfile, db

def seed_personas():
    """Seed initial persona profiles"""
    if PersonaProfile.query.count() == 0:
        # Create sample personas
        pass
```