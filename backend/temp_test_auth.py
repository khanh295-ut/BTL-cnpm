import json
import urllib.request
import urllib.error

base = 'http://127.0.0.1:5000/api'
url = base + '/auth/register'
data = {
    'username': 'testuser123',
    'email': 'testuser123@example.com',
    'password': 'TestPass123',
    'full_name': 'Test User',
    'bio': 'Testing'
}

req = urllib.request.Request(
    url,
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
)
try:
    resp = urllib.request.urlopen(req, timeout=10)
    print('STATUS', resp.status)
    print(resp.read().decode())
except urllib.error.HTTPError as e:
    print('ERR', e.code)
    print(e.read().decode())
except Exception as e:
    print('EXC', str(e))
