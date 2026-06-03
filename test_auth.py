from app import create_app
from models import db

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    from app import create_sample_data
    create_sample_data()

with app.test_client() as client:
    resp = client.post('/auth/register', json={'username': 'testuser', 'email': 'testuser@example.com', 'password': 'Test@1234'})
    print('register', resp.status_code, resp.json)
    resp = client.post('/auth/login', json={'login': 'testuser', 'password': 'Test@1234'})
    print('login', resp.status_code, resp.json)
    resp2 = client.get('/user/profile')
    print('profile', resp2.status_code, resp2.json)
