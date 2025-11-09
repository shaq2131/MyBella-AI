import sys
sys.path.insert(0, '.')
from backend import create_app
from backend.database.models.models import PersonaProfile
app, _ = create_app()
with app.app_context():
    print('hasattr:', hasattr(PersonaProfile, 'communication_style'))
