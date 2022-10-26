from urllib import response
from fastapi.testclient import TestClient
from pathlib import Path
import os

from requests import request

from models import author
os.chdir(Path.cwd().parent)
from main import app, startup_db_client, shutdown_db_client

client = TestClient(app)

def test_read_main():
    '''An example unit test'''
    response = client.get("/")
    assert response.status_code == 200

################################################################### Author tests ##################################################################
def test_add_author():
    '''Add author via post request'''
    # TODO: probably remove this test in future when starts using data import to database directly 
    startup_db_client()

    response = client.post(f"/service/authors/{Fake_Author['id']}",headers={"Content-Type":"application/json"}, json = Fake_Author)
    author = response.json()
    assert response.status_code == 200
    assert author["_id"] == Fake_Author["id"]

    shutdown_db_client()

def test_get_one_author():
    '''Get added author'''
    startup_db_client()
    response = client.get(f"/service/authors/{Fake_Author['id']}",headers={"Content-Type":"application/json"}, json = Fake_Author)
    author = response.json()
    assert response.status_code==200
    assert author["id"] == Fake_Author["id"]

def test_get_authors():
    startup_db_client()
    '''Use get method to get all authors in one time'''
    Fake_Author2 = {
                    "id": "fakeid2",
                    "url":"http://127.0.0.1:5454/authors/fakeauthor2",
                    "host":"http://127.0.0.1:8000/",
                    "displayName":"Fake Thompson",
                    "github": "http://github.com/fakeThopson",
                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                }
    client.post(f"/service/authors/{Fake_Author2['id']}",headers={"Content-Type":"application/json"}, json = Fake_Author2)
    
    response = client.get(f"/service/authors/",headers={"Content-Type":"application/json"})
    authors = response.json()
    for i in range(len(authors)):
        authors[i] = authors[i]["id"]
    assert response.status_code == 200
    assert Fake_Author["id"] in authors
    assert Fake_Author2["id"] in authors
    shutdown_db_client()

def test_update_author():
    startup_db_client()
    '''Update an author's attribute via post method'''
    Fake_Author_Modified = {
                    "id": "fakeid1",
                    "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                    "host":"http://127.0.0.1:8000/",
                    "displayName":"Modified Croft",
                    "github": "http://github.com/modified",
                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                }
    response = client.post(f"/service/authors/{Fake_Author_Modified['id']}",headers={"Content-Type":"application/json"}, json = Fake_Author_Modified)
    author = response.json()
    assert response.status_code == 200
    assert author["displayName"]== Fake_Author_Modified["displayName"]
    assert author["github"]== Fake_Author_Modified["github"]

    # remove fake authors
    app.database["authors"].delete_one({"_id":"fakeid1"})
    app.database["authors"].delete_one({"_id":"fakeid2"})
    app.database["authorManagers"].delete_many({"owner":"fakeid1"})
    app.database["authorManagers"].delete_many({"owner":"fakeid2"})
    shutdown_db_client()


################################################################### Posts tests ##################################################################
def test_add_post():
    '''Adding a test posts'''
    startup_db_client()

    response = client.put(f"/service/authors/'fakeAuthor'/posts/{Fake_Post['id']}",headers={"Content-Type":"application/json"}, json = Fake_Post)
    post = response.json()
    # print(post)
    assert response.status_code == 200
    assert post["_id"] == Fake_Post["id"]

    shutdown_db_client()

def test_add_post_again():
    '''This should receive a 403 for duplicate posts'''
    startup_db_client()
    response = client.put(f"/service/authors/'fakeAuthor'/posts/{Fake_Post['id']}",headers={"Content-Type":"application/json"}, json = Fake_Post)
    assert response.status_code == 403
    shutdown_db_client()
###
def test_delete_post():
    '''Should return 404 once searching for a deleted document'''
    startup_db_client()
    client.delete(f"/service/authors/'fakeAuthor'/posts/{Fake_Post['id']}",headers={"Content-Type":"application/json"}, json = Fake_Post)
    response = client.get(f"/service/authors/'fakeAuthor'/posts/{Fake_Post['id']}",headers={"Content-Type":"application/json"}, json = Fake_Post)
    assert response.status_code == 404 
    shutdown_db_client()



##############################################################################Followers########################################################################################################
def test_get_followers():
    'get a list of authors who are AUTHOR_ID’s followers'
    pass


##########################################Comments###########################################################
def test_add_comment():
    '''Adding a test comment'''
    startup_db_client()
    
    
    response = client.put(f"/service/authors/'fakeAuthor'/posts/'fakepost'/comments/{Fake_Comments['id']}",headers={"Content-Type":"application/json"}, json = Fake_Comments)
    comment = response.json()
    assert response.status_code ==200
    #404
    shutdown_db_client()
    # print(post)
    

def test_get_comments():
    "get a list of comments"
    pass

Fake_Author = {
    "id": "fakeid1",
    "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
    "host":"http://127.0.0.1:8000/",
    "displayName":"Fake Croft",
    "github": "http://github.com/laracroft",
    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
}

Fake_Post = {
            "type":"post",
            "title":"A post title about a post about web dev",
            "id":"fakeid1",
            "source":"posts_routes_test.py",
            # where is it actually from
            "origin":"unit test for posts",
            "description":"This post is used for unit test",
            "contentType":"text/plain",
            "content":"Þā wæs on burgum Bēowulf Scyldinga, lēof lēod-cyning, longe þrāge folcum gefrǣge (fæder ellor hwearf, aldor of earde), oð þæt him eft onwōc hēah Healfdene; hēold þenden lifde, gamol and gūð-rēow, glæde Scyldingas. Þǣm fēower bearn forð-gerīmed in worold wōcun, weoroda rǣswan, Heorogār and Hrōðgār and Hālga til; hȳrde ic, þat Elan cwēn Ongenþēowes wæs Heaðoscilfinges heals-gebedde. Þā wæs Hrōðgāre here-spēd gyfen, wīges weorð-mynd, þæt him his wine-māgas georne hȳrdon, oð þæt sēo geogoð gewēox, mago-driht micel. Him on mōd bearn, þæt heal-reced hātan wolde, medo-ærn micel men gewyrcean, þone yldo bearn ǣfre gefrūnon, and þǣr on innan eall gedǣlan geongum and ealdum, swylc him god sealde, būton folc-scare and feorum gumena. Þā ic wīde gefrægn weorc gebannan manigre mǣgðe geond þisne middan-geard, folc-stede frætwan. Him on fyrste gelomp ǣdre mid yldum, þæt hit wearð eal gearo, heal-ærna mǣst; scōp him Heort naman, sē þe his wordes geweald wīde hæfde. Hē bēot ne ālēh, bēagas dǣlde, sinc æt symle. Sele hlīfade hēah and horn-gēap: heaðo-wylma bād, lāðan līges; ne wæs hit lenge þā gēn þæt se ecg-hete āðum-swerian 85 æfter wæl-nīðe wæcnan scolde. Þā se ellen-gǣst earfoðlīce þrāge geþolode, sē þe in þȳstrum bād, þæt hē dōgora gehwām drēam gehȳrde hlūdne in healle; þǣr wæs hearpan swēg, swutol sang scopes. Sægde sē þe cūðe frum-sceaft fīra feorran reccan",
            "author":{
                "type":"author",
                "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "host":"http://127.0.0.1:5454/",
                "displayName":"Lara Croft",
                "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "github": "http://github.com/laracroft",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
            },
            "categories":["web","tutorial"],
            "count": 1023,
            "comments":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments",
            "commentsSrc":{
                "type":"comments",
                "page":1,
                "size":5,
                "post":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
                "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments",
                "comments":[
                    {
                        "type":"comment",
                        "author":{
                            "type":"author",
                            "id":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                            "url":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                            "host":"http://127.0.0.1:5454/",
                            "displayName":"Greg Johnson",
                            "github": "http://github.com/gjohnson",
                            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                        },
                        "comment":"Sick Olde English",
                        "contentType":"text/markdown",
                        "published":"2015-03-09T13:07:04+00:00",
                        "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments/f6255bb01c648fe967714d52a89e8e9c",
                    }
                ]
            },
            "published":"2015-03-09T13:07:04+00:00",
            "visibility":"PUBLIC",
            "unlisted":"false"
        }


Fake_Follower = {
    "type": "followers",      
    "items":[
        {
            "type":"author",
            "id":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
            "url":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
            "host":"http://127.0.0.1:5454/",
            "displayName":"Greg Johnson",
            "github": "http://github.com/gjohnson",
            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
        },
        {
            "type":"author",
            "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
            "host":"http://127.0.0.1:5454/",
            "displayName":"Lara Croft",
            "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
            "github": "http://github.com/laracroft",
            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
        }
    ]
}



Fake_Comments = {
    "type":"comments",
    "page":1,
    "size":5,
    "post":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
    "id":"fakeid1",
    "comments":[
        {
            "type":"comment",
            "author":{
                "type":"author",
                # ID of the Author (UUID)
                "id":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                # url to the authors information
                "url":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                "host":"http://127.0.0.1:5454/",
                "displayName":"Greg Johnson",
                # HATEOS url for Github API
                "github": "http://github.com/gjohnson",
                # Image from a public domain
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
            },
            "comment":"Sick Olde English",
            "contentType":"text/markdown",
            # ISO 8601 TIMESTAMP
            "published":"2015-03-09T13:07:04+00:00",
            # ID of the Comment (UUID)
            "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments/f6255bb01c648fe967714d52a89e8e9c",
        }
    ]
}

