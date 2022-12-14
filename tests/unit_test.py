from urllib import response
from fastapi.testclient import TestClient
from pathlib import Path
import os
import pytest
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

def test_template_responses():
    response = client.get("/")
    assert response.status_code == 200
    assert response.template.name == 'login.html'
    assert "request" in response.context

################################################################### Author tests ##################################################################
def test_add_author():
    '''Add author via post request'''
    # TODO: probably remove this test in future when starts using data import to database directly
    startup_db_client()

    response = client.post(f"/service/authors/{Fake_Author['id']}",
                           headers={"Content-Type":"application/json"},
                           json=Fake_Author)
    assert response.status_code == 200

    author = response.json()
    assert author["id"] == Fake_Author["id"]


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
                    "hashedPassword": "as#!%lls"
                }
    client.post(f"/service/authors/{Fake_Author2['id']}",headers={"Content-Type":"application/json"}, json = Fake_Author2)

    response = client.get(f"/service/authors/",headers={"Content-Type":"application/json"})
    authors = response.json()["items"]
    for i in range(len(authors)):
        authors[i] = authors[i]["id"]
    assert response.status_code == 200
    assert Fake_Author["id"] in authors
    assert Fake_Author2["id"] in authors


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
                    "hashedPassword": "as#!%lls"
                }
    response = client.post(f"/service/authors/{Fake_Author_Modified['id']}",headers={"Content-Type":"application/json"}, json = Fake_Author_Modified)
    author = response.json()
    assert response.status_code == 200
    assert author["displayName"]== Fake_Author_Modified["displayName"]
    assert author["github"]== Fake_Author_Modified["github"]

    # remove fake authors
    db.delete_author("fakeid1")
    db.delete_author("fakeid2")



################################################################### Posts tests ##################################################################
def test_add_post():
    '''Adding a test post'''
    startup_db_client()
    # Add author
    response = client.post(f"/service/authors/{Fake_Author['id']}", headers={"Content-Type": "application/json"}, json=Fake_Author)

    # Add post
    response = client.put(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}",
                          headers={"Content-Type":"application/json"}, json=Fake_Post)
    response = client.get(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}")
    post = response.json()
    assert response.status_code == 200
    assert post["id"] == Fake_Post["id"]



def test_add_post_again():
    '''This should receive a 400 for duplicate posts'''
    startup_db_client()
    response = client.put(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}",headers={"Content-Type": "application/json"}, json=Fake_Post)
    assert response.status_code == 400


def test_add_no_id_post():
    '''This method adds a post without id, host should generate one for it'''
    startup_db_client()

    # Check we added successfully
    response = client.post(f"/service/authors/{Fake_Author['id']}/posts/",
                           headers={"Content-Type": "application/json"},
                           json=Fake_Post_no_id)
    assert response.status_code == 200

    # Check it was truly added
    post = response.json()
    same_post = client.get(f"/service/authors/{Fake_Author['id']}/posts/{post['id']}").json()
    assert post == same_post

def test_get_posts():
    '''This method should fetch all posts from one user'''
    response = client.get(f"/service/authors/{Fake_Author['id']}/posts/").json()

    assert len(response.keys()), 2
    assert "fakeid1" in response.keys()

def test_update_post():
    '''This method should update one attribute in post that belongs to a user'''
    # pytest.set_trace()
    response = client.post(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}/",
                           headers={"Content-Type": "application/json"},
                           json=Fake_Post_modified,allow_redirects=False)
    modified_post = client.get(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}").json()

    assert response.status_code == 200
    assert modified_post['title'] == "This post is modified"

def test_delete_post():
    '''Should return 404 once searching for a deleted document'''
    startup_db_client()
    client.delete(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}",
                  headers={"Content-Type": "application/json"}, json=Fake_Post)

    # Check post was deleted
    response = client.get(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}")
    assert response.status_code == 404

    # Delete the author as well
    db.delete_author("fakeid1")



##############################################################################Followers########################################################################################################

def test_add_followers():
    startup_db_client()
    response = client.post(f"/service/authors/{Fake_Author['id']}",headers={"Content-Type":"application/json"}, json = Fake_Author)
    assert response.status_code == 200
    # add one fakeauthor2 as a follower of fake author 1
    response = client.put(f"/service/authors/{Fake_Author['id']}/followers/{Fake_Author2['id']}",headers={"Content-Type":"application/json"}, json = Fake_Author2)
    assert response.status_code == 200
    follower = response.json()
    assert follower['foreign_author_id']== Fake_Author2['id']


def test_check_followers():
    '''
    Check if foreign author id is a follower of author id, return message if so
    otherwise return error
    '''
    startup_db_client()
    response = client.get(f"/service/authors/{Fake_Author['id']}/followers/{Fake_Author2['id']}")
    assert response.status_code == 200

    follower = response.json()
    assert follower['foreign_author_id']==Fake_Author2['id']


def test_read_followers():
    startup_db_client()
    Fake_Author3 = {
    "id": "fakeid3",
    "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
    "host":"http://127.0.0.1:8000/",
    "displayName":"Fake Croft",
    "github": "http://github.com/laracroft",
    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
    "hashedPassword": "as#!%lls"
}

    client.post(f"/service/authors/{Fake_Author2['id']}",
                headers={"Content-Type":"application/json"}, json=Fake_Author2)
    client.post(f"/service/authors/{Fake_Author3['id']}",
                headers={"Content-Type":"application/json"}, json=Fake_Author3)

    response = client.put(f"/service/authors/{Fake_Author['id']}/followers/{Fake_Author3['id']}",headers={"Content-Type":"application/json"}, json = Fake_Author3)
    assert response.status_code == 200

    response = client.get(f"/service/authors/{Fake_Author['id']}/followers")
    follower = response.json()
    assert response.status_code == 200
    assert Fake_Author2['id'],Fake_Author3['id'] in follower['item']
    #assert len(follower['items']) == 2
    app.database["authors"].delete_one({"_id":"fakeid3"})


def test_delete_followers():
    startup_db_client()
    client.delete(f"/service/authors/{Fake_Author['id']}/followers/{Fake_Author2['id']}",headers={"Content-Type":"application/json"}, json = Fake_Author2)
    response = client.get(f"/service/authors/{Fake_Author['id']}/followers/{Fake_Author2['id']}")
    assert response.status_code == 404

    app.database["authors"].delete_one({"_id": "fakeid2"})
    app.database["authors"].delete_one({"_id": "fakeid1"})
    app.database["authorManagers"].delete_many({"_id": "fakeid1"})
    app.database["authorManagers"].delete_many({"_id": "fakeid2"})
    app.database["authorManagers"].delete_many({"_id": "fakeid3"})



##########################################Comments###########################################################
def test_add_comment():
    '''Adding a test comment'''
    startup_db_client()
    #add comment author
    client.post(f"/service/authors/{Fake_Author2['id']}",headers={"Content-Type":"application/json"}, json = Fake_Author2)
    #add post author
    client.post(f"/service/authors/{Fake_Author['id']}",headers={"Content-Type":"application/json"}, json = Fake_Author)
    # Add post
    response = client.put(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}",headers={"Content-Type":"application/json"}, json = Fake_Post)

    # Add comment on post
    response = client.post(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}/comments",headers={"Content-Type":"application/json"}, json=Fake_Comments)

    assert response.status_code == 200 #author or post  found



def test_get_comments():
    '''Test get a comment & comments'''
    startup_db_client()

    # get one comment
    comment = client.get(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}/comments").json()
    print(comment["comments"])
    assert comment["comments"][0]["author"]["id"] == "fakeid1"
    assert comment["comments"][0]["comment"] == "fake comment"

    response = client.post(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}/comments",headers={"Content-Type":"application/json"}, json=Fake_Comments)
    assert response.status_code == 200
    comments = client.get(f"/service/authors/{Fake_Author['id']}/posts/{Fake_Post['id']}/comments").json()
    assert len(comments["comments"]) == 2

    app.database["comments"].delete_many({"post":"fakeid1"})
    app.database["authors"].delete_one({"_id": "fakeid1"})
    app.database["authors"].delete_one({"_id": "fakeid2"})
    app.database["post"].delete_one({"_id": "fakeid1"})
    app.database["authorManagers"].delete_many({"_id": "fakeid1"})
    app.database["authorManagers"].delete_many({"_id": "fakeid2"})


def test_like_post():
    startup_db_client()
    response = client.post("")


Fake_Author2 = {
    "id": "fakeid2",
    "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
    "host":"http://127.0.0.1:8000/",
    "displayName":"Fake Croft",
    "github": "http://github.com/laracroft",
    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
    "hashedPassword": "as#!%lls",
    "posts":{}
}
Fake_Author = {
    "id": "fakeid1",
    "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
    "host":"http://127.0.0.1:8000/",
    "displayName":"Fake Croft",
    "github": "http://github.com/laracroft",
    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
    "hashedPassword": "as#!%lls"
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
            "content":"???? w??s on burgum B??owulf Scyldinga, l??of l??od-cyning, longe ??r??ge folcum gefr??ge (f??der ellor hwearf, aldor of earde), o?? ????t him eft onw??c h??ah Healfdene; h??old ??enden lifde, gamol and g????-r??ow, gl??de Scyldingas. ????m f??ower bearn for??-ger??med in worold w??cun, weoroda r??swan, Heorog??r and Hr????g??r and H??lga til; hy??rde ic, ??at Elan cw??n Ongen????owes w??s Hea??oscilfinges heals-gebedde. ???? w??s Hr????g??re here-sp??d gyfen, w??ges weor??-mynd, ????t him his wine-m??gas georne hy??rdon, o?? ????t s??o geogo?? gew??ox, mago-driht micel. Him on m??d bearn, ????t heal-reced h??tan wolde, medo-??rn micel men gewyrcean, ??one yldo bearn ??fre gefr??non, and ????r on innan eall ged??lan geongum and ealdum, swylc him god sealde, b??ton folc-scare and feorum gumena. ???? ic w??de gefr??gn weorc gebannan manigre m??g??e geond ??isne middan-geard, folc-stede fr??twan. Him on fyrste gelomp ??dre mid yldum, ????t hit wear?? eal gearo, heal-??rna m??st; sc??p him Heort naman, s?? ??e his wordes geweald w??de h??fde. H?? b??ot ne ??l??h, b??agas d??lde, sinc ??t symle. Sele hl??fade h??ah and horn-g??ap: hea??o-wylma b??d, l????an l??ges; ne w??s hit lenge ???? g??n ????t se ecg-hete ????um-swerian 85 ??fter w??l-n????e w??cnan scolde. ???? se ellen-g??st earfo??l??ce ??r??ge ge??olode, s?? ??e in ??y??strum b??d, ????t h?? d??gora gehw??m dr??am gehy??rde hl??dne in healle; ????r w??s hearpan sw??g, swutol sang scopes. S??gde s?? ??e c????e frum-sceaft f??ra feorran reccan",
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
            "content":"???? w??s on burgum B??owulf Scyldinga, l??of l??od-cyning, longe ??r??ge folcum gefr??ge (f??der ellor hwearf, aldor of earde), o?? ????t him eft onw??c h??ah Healfdene; h??old ??enden lifde, gamol and g????-r??ow, gl??de Scyldingas. ????m f??ower bearn for??-ger??med in worold w??cun, weoroda r??swan, Heorog??r and Hr????g??r and H??lga til; hy??rde ic, ??at Elan cw??n Ongen????owes w??s Hea??oscilfinges heals-gebedde. ???? w??s Hr????g??re here-sp??d gyfen, w??ges weor??-mynd, ????t him his wine-m??gas georne hy??rdon, o?? ????t s??o geogo?? gew??ox, mago-driht micel. Him on m??d bearn, ????t heal-reced h??tan wolde, medo-??rn micel men gewyrcean, ??one yldo bearn ??fre gefr??non, and ????r on innan eall ged??lan geongum and ealdum, swylc him god sealde, b??ton folc-scare and feorum gumena. ???? ic w??de gefr??gn weorc gebannan manigre m??g??e geond ??isne middan-geard, folc-stede fr??twan. Him on fyrste gelomp ??dre mid yldum, ????t hit wear?? eal gearo, heal-??rna m??st; sc??p him Heort naman, s?? ??e his wordes geweald w??de h??fde. H?? b??ot ne ??l??h, b??agas d??lde, sinc ??t symle. Sele hl??fade h??ah and horn-g??ap: hea??o-wylma b??d, l????an l??ges; ne w??s hit lenge ???? g??n ????t se ecg-hete ????um-swerian 85 ??fter w??l-n????e w??cnan scolde. ???? se ellen-g??st earfo??l??ce ??r??ge ge??olode, s?? ??e in ??y??strum b??d, ????t h?? d??gora gehw??m dr??am gehy??rde hl??dne in healle; ????r w??s hearpan sw??g, swutol sang scopes. S??gde s?? ??e c????e frum-sceaft f??ra feorran reccan",
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
            "content":"???? w??s on burgum B??owulf Scyldinga, l??of l??od-cyning, longe ??r??ge folcum gefr??ge (f??der ellor hwearf, aldor of earde), o?? ????t him eft onw??c h??ah Healfdene; h??old ??enden lifde, gamol and g????-r??ow, gl??de Scyldingas. ????m f??ower bearn for??-ger??med in worold w??cun, weoroda r??swan, Heorog??r and Hr????g??r and H??lga til; hy??rde ic, ??at Elan cw??n Ongen????owes w??s Hea??oscilfinges heals-gebedde. ???? w??s Hr????g??re here-sp??d gyfen, w??ges weor??-mynd, ????t him his wine-m??gas georne hy??rdon, o?? ????t s??o geogo?? gew??ox, mago-driht micel. Him on m??d bearn, ????t heal-reced h??tan wolde, medo-??rn micel men gewyrcean, ??one yldo bearn ??fre gefr??non, and ????r on innan eall ged??lan geongum and ealdum, swylc him god sealde, b??ton folc-scare and feorum gumena. ???? ic w??de gefr??gn weorc gebannan manigre m??g??e geond ??isne middan-geard, folc-stede fr??twan. Him on fyrste gelomp ??dre mid yldum, ????t hit wear?? eal gearo, heal-??rna m??st; sc??p him Heort naman, s?? ??e his wordes geweald w??de h??fde. H?? b??ot ne ??l??h, b??agas d??lde, sinc ??t symle. Sele hl??fade h??ah and horn-g??ap: hea??o-wylma b??d, l????an l??ges; ne w??s hit lenge ???? g??n ????t se ecg-hete ????um-swerian 85 ??fter w??l-n????e w??cnan scolde. ???? se ellen-g??st earfo??l??ce ??r??ge ge??olode, s?? ??e in ??y??strum b??d, ????t h?? d??gora gehw??m dr??am gehy??rde hl??dne in healle; ????r w??s hearpan sw??g, swutol sang scopes. S??gde s?? ??e c????e frum-sceaft f??ra feorran reccan",
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
            "type": "comment",
            "_id":  'fakeid1',
            "author": "fakeid2", # Author ID of the post
            "post": 'fakeid1',#ObjectId of the post
            "comment":  'fake comment',
            "contentType": "text/markdown",
            "published": '2022-10-25T11:09:11.383160'
        }

