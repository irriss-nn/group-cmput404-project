from urllib import response
from fastapi.testclient import TestClient
from pathlib import Path
import os

from requests import request

from database import SocialDatabase
from models import author
os.chdir(Path.cwd().parent)
from main import app, startup_db_client, shutdown_db_client

db = SocialDatabase()
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
    assert author["id"] == Fake_Author["id"]

    shutdown_db_client()

def test_get_one_author():
    '''Get added author'''
    startup_db_client()
    response = client.get(f"/service/authors/{Fake_Author['id']}")
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
                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                    "hashedPassword": "as#!%lls",
                    "posts":{}
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
                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                    "hashedPassword": "as#!%lls",
                    "posts":{}
                }
    response = client.post(f"/service/authors/{Fake_Author_Modified['id']}",headers={"Content-Type":"application/json"}, json = Fake_Author_Modified)
    author = response.json()
    assert response.status_code == 200
    assert author["displayName"]== Fake_Author_Modified["displayName"]
    assert author["github"]== Fake_Author_Modified["github"]

    # remove fake authors
    db.delete_author("fakeid1")
    db.delete_author("fakeid2")
    shutdown_db_client()


################################################################### Posts tests ##################################################################
def test_add_post():
    '''Adding a test post'''
    startup_db_client()
    # Add author
    response = client.post(f"/service/authors/{Fake_Author['id']}",headers={"Content-Type":"application/json"}, json = Fake_Author)

    # Add post
    response = client.put(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}",headers={"Content-Type":"application/json"}, json = Fake_Post)
    response = client.get(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}")
    post = response.json()
    assert response.status_code == 200
    assert post["id"] == Fake_Post["id"]

    shutdown_db_client()

def test_add_post_again():
    '''This should receive a 403 for duplicate posts'''
    startup_db_client()
    response = client.put(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}",headers={"Content-Type":"application/json"}, json = Fake_Post)
    assert response.status_code == 403
    shutdown_db_client()

def test_add_no_id_post():
    '''This method adds a post without id, host should generate one for it'''
    startup_db_client()
    author_before = client.get(f"/service/authors/{Fake_Author['id']}").json()
    response = client.post(f"/service/authors/{Fake_Author['id']}/posts/",headers={"Content-Type":"application/json"}, json = Fake_Post_no_id)
    author = client.get(f"/service/authors/{Fake_Author['id']}")
    author = author.json()
    assert len(author["posts"]), len(author_before["posts"])+1
    assert response.status_code == 200

def test_get_posts():
    '''This method should fetch all psots from one user'''
    response = client.get(f"/service/authors/{Fake_Author['id']}/posts/").json()
    
    assert len(response.keys()), 2
    assert "fakeid1" in response.keys()

def test_update_post():
    '''This method should update one attribute in post that belongs to a user'''
    response = client.post(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}",headers={"Content-Type":"application/json"}, json = Fake_Post_modified)
    modified_post = client.get(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}").json()

    assert response.status_code == 200
    assert modified_post['title'] == "This post is modified"

def test_delete_post():
    '''Should return 404 once searching for a deleted document'''
    startup_db_client()
    client.delete(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}",headers={"Content-Type":"application/json"}, json = Fake_Post)
    response = client.get(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}")

    # Delete the author as well
    db.delete_author("fakeid1")
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
    
    
    response = client.post(f"/service/authors/'fakeAuthor'/posts/'fakePost'/comments/",headers={"Content-Type":"application/json"}, json = Fake_Comments)
    #post fail
    #response = client.get(f"/service/authors/'fakeAuthor'/posts/'fakePost'/comments/",headers={"Content-Type":"application/json"}, json = Fake_Comments)
    #comment = response.json()
    assert response.status_code ==200
    #assert comment["id"]== "fakeid1"
    
    shutdown_db_client()
    
    
def test_get_comments():
    startup_db_client()
    response = client.get(f"/service/authors/'fakeAuthor'/posts/'fakePost'/comments/",headers={"Content-Type":"application/json"}, json = Fake_Comments)
    comment = response.json()
    shutdown_db_client()


Fake_Author = {
    "id": "fakeid1",
    "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
    "host":"http://127.0.0.1:8000/",
    "displayName":"Fake Croft",
    "github": "http://github.com/laracroft",
    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
    "hashedPassword": "as#!%lls",
    "posts":{}
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

Fake_Post_modified = {
            "type":"post",
            "title":"This post is modified",
            "id":"fakeid1",
            "source":"unit_test.py modified method",
            # where is it actually from
            "origin":"unit test for modified posts",
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

Fake_Post_no_id = {
            "type":"post",
            "title":"A post doesn't have id!",
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
            "comment":  "sick olde Englsih"
           }
     

