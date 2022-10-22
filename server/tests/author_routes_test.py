from urllib import response
from fastapi.testclient import TestClient
import sys
sys.path.append('../server')
from server.app import app, startup_db_client, shutdown_db_client
# from server.routers import authors

client = TestClient(app)


def test_add_author():
    Fake_Author = {
        "id": "fakeid1",
        "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
        "host":"http://127.0.0.1:8000/",
        "displayName":"Fake Croft",
        "github": "http://github.com/laracroft",
        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
    }
    startup_db_client()

    response = client.post("/service/authors/",headers={"Content-Type":"application/json"}, json = Fake_Author)
    author = response.json()
    print(author)
    assert response.status_code == 200
    assert author["_id"] == Fake_Author["id"]

    shutdown_db_client()