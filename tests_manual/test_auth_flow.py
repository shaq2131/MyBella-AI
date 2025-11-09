import sys
sys.path.insert(0, '.')

from backend import create_app

app, socketio = create_app()

client = app.test_client()

# GET login
resp = client.get('/login')
print('GET /login', resp.status_code)

# POST login with invalid
resp = client.post('/login', data={'email':'none@example.com','password':'pass'}, follow_redirects=True)
print('POST /login invalid', resp.status_code)

# POST register minimal valid
from datetime import date
form = {
    'username':'testuser_cli',
    'email':'test_cli@example.com',
    'gender':'male',
    'date_of_birth': '2000-01-01',
    'password': 'password123',
    'confirm_password':'password123',
    'terms':'on'
}
resp = client.post('/register', data=form, follow_redirects=True)
print('POST /register', resp.status_code)
print('Contains dashboard?', b'Dashboard' in resp.data)
