from urllib import response
from fastapi.testclient import TestClient
import sys
sys.path.append('../server')
from server.app import app, startup_db_client, shutdown_db_client
# from server.routers import authors

client = TestClient(app)

Fake_Author = {
    "id": "fakeid1",
    "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
    "host":"http://127.0.0.1:8000/",
    "displayName":"Fake Croft",
    "github": "http://github.com/laracroft",
    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
}

def test_add_author():
    '''Add author via post request'''
    # TODO: probably remove this test in future when starts using data import to database directly 
    startup_db_client()

    response = client.post("/service/authors/",headers={"Content-Type":"application/json"}, json = Fake_Author)
    author = response.json()
    assert response.status_code == 200
    assert author["_id"] == Fake_Author["id"]

    #shutdown_db_client()

def test_get_one_author():
    '''Get added author'''
    startup_db_client()
    response = client.get(f"/service/authors/{Fake_Author['id']}",headers={"Content-Type":"application/json"}, json = Fake_Author)
    author = response.json()
    print('hhhhhhhh',author)
    assert response.status_code==200
    assert author["author_id"] == Fake_Author["id"]

def test_get_authors():
    '''Use get method to get all authors in one time'''
    Fake_Author2 = {
                    "id": "fakeid2",
                    "url":"http://127.0.0.1:5454/authors/fakeauthor2",
                    "host":"http://127.0.0.1:8000/",
                    "displayName":"Fake Thompson",
                    "github": "http://github.com/fakeThopson",
                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                }
    client.post("/service/authors/",headers={"Content-Type":"application/json"}, json = Fake_Author2)
    
    response = client.get(f"/service/authors/{Fake_Author['id'],Fake_Author2['id']}",headers={"Content-Type":"application/json"}, json = Fake_Author)
    authors = response.json()
    assert response.status_code == 200
    assert "('fakeid1', 'fakeid2')" in authors["author_id"] 
    #print('yyyyyyyuuuuuuuuuu',author)

    

def test_update_author():
    '''Update an author's attribute via post method'''
    Fake_Author_Modified = {
                    "id": "fakeid1",
                    "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                    "host":"http://127.0.0.1:8000/",
                    "displayName":"Modified Croft",
                    "github": "http://github.com/modified",
                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                }
    response = client.post("/service/authors/",headers={"Content-Type":"application/json"}, json = Fake_Author_Modified)
    author = response.json()
    assert response.status_code == 200
    assert author["_id"] == Fake_Author["id"]