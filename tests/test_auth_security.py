from app.auth import hash_password, verify_password
from app.main import safe_csv


def test_password_hashes_salted_and_verifiable():
    a,b=hash_password('StrongTest@2026'),hash_password('StrongTest@2026')
    assert a!=b and verify_password('StrongTest@2026',a)
    assert not verify_password('incorrect',a)


def test_unauthenticated_endpoints_protected(client):
    for url in ['/api/tickets','/api/dashboard','/api/ai/model-card','/api/users/assignees','/api/export/tickets.csv']:
        assert client.get(url).status_code == 401
    assert client.post('/api/tickets',json={}).status_code in (401,422)


def test_auth_failure_and_signout(client):
    assert client.post('/api/auth/login',json={'email':'student@campusrelay.demo','password':'WrongPass!!'}).status_code==401
    login=client.post('/api/auth/login',json={'email':'student@campusrelay.demo','password':'Student@2026!'})
    assert login.status_code==200
    assert 'HttpOnly' in login.headers['set-cookie'] and 'samesite=lax' in login.headers['set-cookie'].lower()
    assert client.get('/api/auth/me').status_code==200
    assert client.post('/api/auth/logout',json={},headers={'X-CSRF-Token':login.json()['csrf_token']}).status_code==200
    assert client.get('/api/auth/me').status_code==401


def test_register_is_student_only_and_rejects_duplicates(client):
    body={'name':'New Learner','email':'learner@example.edu','password':'StrongPassword2026'}
    assert client.post('/api/auth/register',json=body).status_code==201
    assert client.post('/api/auth/register',json=body).status_code==409
    login=client.post('/api/auth/login',json={'email':body['email'],'password':body['password']})
    assert login.status_code==200 and login.json()['user']['role']=='student'


def test_register_validation(client):
    assert client.post('/api/auth/register',json={'name':'X','email':'invalid','password':'short'}).status_code==422
    assert client.post('/api/auth/register',json={'name':'New Learner','email':'new@example.org','password':'passwordpassword','role':'admin'}).status_code==422


def test_csrf_guard_prevents_mutations(student):
    client,_=student
    body={'title':'The wireless access is down','description':'Wi-Fi is unavailable in our computer lab for the entire morning.','location':'Computer Lab 3','category':'IT','priority':'High'}
    assert client.post('/api/tickets',json=body).status_code==403
    assert client.post('/api/ai/suggest',json={'text':'the bus did not arrive at our stop on time'}).status_code==403
    assert client.post('/api/auth/logout',json={}).status_code==403


def test_unsafe_content_type_and_cross_origin_are_rejected(client):
    response=client.post('/api/auth/login',content='hello',headers={'Content-Type':'text/plain'})
    assert response.status_code==415, response.text
    response=client.post('/api/auth/login',json={'email':'x@y.io','password':'a'},headers={'Origin':'https://attacker.example'})
    assert response.status_code==403, response.text


def test_login_rate_limit(client):
    for i in range(8):
        r=client.post('/api/auth/login',json={'email':'unknown@example.test','password':'wrong-password'})
        assert r.status_code==401
    assert client.post('/api/auth/login',json={'email':'unknown@example.test','password':'wrong-password'}).status_code==429


def test_csv_formula_injection_guard():
    assert safe_csv('=cmd|A0')=="'=cmd|A0"
    assert safe_csv('  @SUM(A1)')=="'  @SUM(A1)"
    assert safe_csv('normal campus issue')=='normal campus issue'


def test_security_headers(client):
    res=client.get('/')
    assert res.status_code==200
    assert res.headers['x-frame-options']=='DENY'
    assert "script-src 'self'" in res.headers['content-security-policy']
    assert client.get('/static/app.js').status_code==200
    assert client.get('/static/styles.css').status_code==200
