import datetime
import uuid

from pydantic import BaseModel, Field

class InboxItem(BaseModel):
    type: str = "InboxItem"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: str = "Notification" # Possible values: "Notification(post like, comment like)", "Request"
    actionDescription: str = "A new activity has been performed"
    actionReference: str = "" # ID of the post/comment that was liked, or ID of the person requesting to follow
    actionNeeded: bool = False # True if the user needs to do something for exmaple accept the request
    actionValues: dict = {} # Values that are needed to perform the action for exmaple {"Accept": "{url_to_accept_request}", {"Reject": "{url_to_reject_request}"}

    time: str = datetime.datetime.now().isoformat()

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                        "action":"Request",
                        "actionDescription": "You have a new follow request",
                        "actionReference":"4c8095ad-7d95-48fc-b9a2-53464d014d8e",
                        "actionNeeded":True,
                        "actionValues":{"Accept":"/author/accept/4c8095ad-7d95-48fc-b9a2-53464d014d8e","Reject":"/author/reject/4c8095ad-7d95-48fc-b9a2-53464d014d8e"}
            }
            }
