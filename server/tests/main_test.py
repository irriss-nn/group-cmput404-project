from fastapi.testclient import TestClient
import sys
sys.path.append('../server')
from server.app import app

client = TestClient(app)

def test_read_main():
    '''An example unit test'''
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}