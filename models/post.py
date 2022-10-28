import uuid

from dataclasses import dataclass

@dataclass
class Post:
    title: str 
    source: str
    origin: str 
    description: str 
    contentType: str 
    content: str
    author: dict|None  # TODO: Remove
    categories: list
    count: int
    comments: str  # TODO: Should be list
    commentSrc: dict | None
    published: str
    visibility: str
    unlisted: str
    id: str | None = str(uuid.uuid4())

    @staticmethod
    def init_with_dict(data: dict):
        return Post(
                    id=data["_id"],
                    title=data["title"],
                    source=data["source"],
                    origin=data["origin"],
                    description=data["description"],
                    contentType=data["contentType"],
                    content=data["content"],
                    author=data["author"],
                    categories=data["categories"],
                    count=data["count"],
                    comments=data["comments"],
                    commentSrc=data["commentSrc"],
                    published=data["published"],
                    visibility=data["visibility"],
                    unlisted=data["unlisted"])

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "type":"post",
                "title":"A post title about a post about web dev",
                "id":"764efa883dda1e11db47671c4a3bbd9e",
                "source":"http://lastplaceigotthisfrom.com/posts/yyyyy",
                # where is it actually from
                "origin":"http://whereitcamefrom.com/posts/zzzzz",
                "description":"This post discusses stuff -- brief",
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
        }
