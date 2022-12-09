from fastapi import APIRouter, HTTPException, Request, status, Cookie
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from database import SocialDatabase
from models.author import Author
from models.inbox import InboxItem

static_dir = f"{Path.cwd()}/static"
templates = Jinja2Templates(directory=f"{static_dir}/templates")
router = APIRouter(
    prefix="/service/authors",
    tags=["author"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def read_authors(page: int | None = 0, size: int | None = 0):
    if page is None or size is None:
        authors = SocialDatabase().get_authors()
    else:
        authors = SocialDatabase().get_authors(page*size, size)

    return {"type": "authors", "items": [author.json() for author in authors]}


@router.post("/{author_id}")
async def create_author(author_id: str, author: Author):
    if author.id != author_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Author ids do not match")

    db = SocialDatabase()
    if not (db.create_author(author) or db.update_author(author)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return author.json()


@router.get("/{author_id}")
async def read_item(author_id: str):
    '''Get author by id'''
    author = SocialDatabase().get_author(author_id)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Author does not exist")

    return author.json()

# Follower functionalities


@router.delete("/{author_id}/followers/{foreign_author_id}")
async def delete_follower(author_id: str, foreign_author_id: str, request: Request):
    '''Delete a follower from authors follower list'''
    request.app.database["authorManagers"].update_one(
        {"_id": author_id}, {"$pull": {"followers": foreign_author_id}})
    return {"message": "Successfully deleted follower", "author_id": author_id, "foreign_author_id": foreign_author_id}


@router.put("/{author_id}/followers/{foreign_author_id}")
async def add_follower(author_id: str, foreign_author_id: str, request: Request):
    '''Add a user to the list of followers of the author'''
    # We need to handle authentication here !!! TO DO !!!
    request.app.database["authorManagers"].update_one(
        {"_id": author_id}, {"$push": {"followers": foreign_author_id}})
    return {"message": "Successfully added follower", "author_id": author_id, "foreign_author_id": foreign_author_id}


@router.delete("/{author_id}/inbox/{inbox_request_id}")
async def delete_inbox(inbox_request_id: str, author_id: str, request: Request):
    '''Delete a inbox item from authors inbox list'''
    request.app.database["authorManagers"].update_one(
        {"_id": author_id}, {"$pull": {"inbox": {"id": inbox_request_id}}})
    return {"message": "Successfully deleted inbox request", "inbox_request_id": inbox_request_id}


@router.get("/{author_id}/followers/{foreign_author_id}")
# Check if foreign author id is a follower of author id, if it is return message if not return error
async def check_follower(author_id: str, foreign_author_id: str, request: Request):
    '''
    Check if foreign author id is a follower of author id, return message if so
    otherwise return error
    '''
    if request.app.database["authorManagers"].find_one({"_id": author_id, "followers": foreign_author_id}):
        return {"message": "Foreign author is a follower of author", "author_id": author_id, "foreign_author_id": foreign_author_id}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Foreign author is not a follower of author")


@router.get("/{author_id}/followers")
async def read_followers(author_id: str, request: Request):
    '''Get a list of all followers of the author'''
    return_list = []
    follower_list = request.app.database["authorManagers"].find_one({
                                                                    "_id": author_id})
    if follower_list is None:
        return {"type": "followers", "items": return_list}
    for objId in follower_list["followers"]:
        return_list.append(
            request.app.database["authors"].find_one({"_id": objId}))
    return {"type": "followers", "items": return_list}


@router.get("/{author_id}/following",
            responses={
                200: {'description': 'Return a list of all authors that an author follows'},
                404: {'description': 'Author does not exist'},
            })
async def get_following_authors(author_id: str):
    '''Return a list of all authors that an author follows'''
    author_manager = SocialDatabase().get_author_manager(author_id)
    if not author_manager:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='Author does not exist')

    author_manager = author_manager.json()
    return {"type": "following", "items": author_manager['following']}


@router.get("/{author_id}/{foreign_author_id}/status")
async def check_follow_status(author_id: str, foreign_author_id: str, request: Request):
    '''As an author, When I befriend someone I follow them, only when the other author befriends me do I count as a real friend'''
    if request.app.database["authorManagers"].find_one({"_id": author_id, "following": {"$in": [foreign_author_id]}}) and request.app.database["authorManagers"].find_one({"_id": foreign_author_id, "following": {"$in": [author_id]}}):
        return {"message": "We are true friends", "author_id": author_id, "foreign_author_id": foreign_author_id}
    elif request.app.database["authorManagers"].find_one({"_id": author_id, "following": {"$in": [foreign_author_id]}}):
        return {"message": "I am just a friend", "author_id": author_id, "foreign_author_id": foreign_author_id}
    else:
        return {"message": "We are not friends", "author_id": author_id, "foreign_author_id": foreign_author_id}

### IMPLEMENT PROJECT SPECS FOR LIKES ###


@router.post("/{author_id}/inbox")
async def add_like_to_inbox(author_id: str, request: Request):
    '''Add a like to the inbox of the author'''
    # We need to handle authentication here !!! TO DO !!!

    return SocialDatabase().create_generic_like_notification(author_id)


@router.get("/{author_id}/posts/{post_id}/likes")
async def get_likes_for_post(author_id: str, post_id: str, request: Request):
    '''Get a list of all likes for a post'''
    return SocialDatabase().get_likes_for_post(post_id, author_id)


@router.get("/{author_id}/posts/{post_id}/comments/{comment_id}/likes")
async def get_likes_on_comment_on_post(author_id: str, post_id: str, comment_id: str, request: Request):
    '''Get a list of all likes for a comment on a post'''
    return SocialDatabase().get_likes_on_comment_on_post(post_id, comment_id, author_id)


@router.get("/inboxsize/{author_id}")
async def get_inbox_size(author_id: str, request: Request):
    '''Get the size of the inbox of the author'''
    return SocialDatabase().get_inbox_size(author_id)

### INBOX RELATED FUNCTIONALITY ###
# Add button to all profiles to send friend request, first author id is the author sending the request, second author id is the author receiving the request
# This will be implemented in the main file too for now
# @router.put("/{author_id}/followers/{foreign_author_id}/request")
# async def add_follower(author_id: str, foreign_author_id: str, request: Request):
#     '''Request a follow to the foreign author'''
#     try:  # To do: check if already there is a request from that author
#         # Create inbox request
#         inbox_item = InboxItem(action="Request", actionDescription="You have a new follow request", actionReference=author_id, actionNeeded=True, actionValues={
#                                "Accept": f"/service/authors/{foreign_author_id}/accept/{author_id}", "Reject": f"/service/authors/{foreign_author_id}/reject/{author_id}"})
#         inbox_item = jsonable_encoder(inbox_item)
#         authorReceivingRequest = SocialDatabase().get_author_manager(foreign_author_id)
#         if (author_id in authorReceivingRequest.requests):  # If alreayd sent the request
#             return {"message": "You have already sent a request to this author"}
#         request.app.database["authorManagers"].update_one({"_id": foreign_author_id}, {
#                                                           "$push": {"inbox": inbox_item, "requests": author_id}})
#         return True
#     except:
#         return False


@router.post("/{author_id}/{action}/{foreign_author}")
async def accept_or_reject_follower(author_id: str, action: str, foreign_author: str, request: Request):
    '''Accept or reject a follow request'''
    if action == "accept":
        # Add the foreign author to the author's followers and remove the request
        request.app.database["authorManagers"].update_one({"_id": author_id}, {
                                                          "$push": {"followers": foreign_author}, "$pull": {"requests": foreign_author}})
        # Add the author to the foreign author's following
        request.app.database["authorManagers"].update_one(
            {"_id": foreign_author}, {"$push": {"following": author_id}})
        # Remove the inbox item
        request.app.database["authorManagers"].update_one(
            {"_id": author_id}, {"$pull": {"inbox": {"actionReference": foreign_author}}})
        # return True
        return RedirectResponse(url='/home')
    elif action == "reject":
        # Remove the request
        request.app.database["authorManagers"].update_one(
            {"_id": author_id}, {"$pull": {"requests": foreign_author}})
        # Remove the inbox item
        request.app.database["authorManagers"].update_one(
            {"_id": author_id}, {"$pull": {"inbox": {"actionReference": foreign_author}}})
        # return True
        return RedirectResponse(url='/home')
    else:
        # return False
        return RedirectResponse(url='/home')

# #### USER FACING VIEWS ####
# @router.get("/{author_id}/view")
# async def read_item(request: Request, author_id: str, session:  str=Cookie(None)):
#     '''
#     Display author profile
#     '''
#     # try:
#     document = SocialDatabase().get_author(author_id)
#     if (document is None):
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
#     return templates.TemplateResponse("author.html", {"request": request, "user": document})
#     # except Exception as e:
#     #     print(e)
#     #     raise HTTPException(
#     #         status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
