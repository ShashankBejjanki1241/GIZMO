import pytest
from app import app

@pytest.fixture()
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_root(client):
    r = client.get('/')
    assert r.status_code == 200
    assert r.get_json()['message'] == 'Hello World'

def test_sum_endpoint(client):
    # Should fail initially: /sum missing
    r = client.get('/sum?x=2&y=3')
    assert r.status_code == 200
    assert r.get_json()['result'] == 5
