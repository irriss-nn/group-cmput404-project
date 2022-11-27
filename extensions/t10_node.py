# Node Protocol Implementation
#
# This protocol is designed to communicate authentication credentials between
# servers.
#
# When a foreign server authenticates with its credentials, the home server
# will verify and reply with whether the credentials are valid.
#
# Original documentation from Team 10 available at:
# https://github.com/hgshah/cmput404-project/tree/staging/docs
#
# NOTE: Possible future protocol issues:
#       - No CSRF tokens
#       - Credentials may change
#           - If not, need to ensure credentials are secured well
#           - Else, need expiry date (and regen credentials afterwards)
#       - Since validation should already happen on other endpoints, this
#         protocol may be redundant

from dataclasses import dataclass, asdict
from fastapi import APIRouter, Depends, Header, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from secrets import compare_digest

from database import SocialDatabase
from models.base import Base

security = HTTPBasic()  # username:password
router = APIRouter(
    # TODO: Would be preferable to prefix with '/service/ext' (amend later?)
    prefix='',
    tags=['extensions']
)


@dataclass
class NodeAuthenticated:
    message: str = 'Authentication Successful'
    type: str = 'remoteNode'


@dataclass
class NodeValidationFail:
    message: str


@dataclass
class Node(Base):
    remote_host: str  # Primary key
    username: str  # Used by us to access remote
    password: str
    remote_username: str  # Used by remote to access us
    remote_password: str
    admin_approved: bool = True  # Always true (otherwise not in db)

    @classmethod
    def init_from_mongo(cls, data: dict):
        data['remote_host'] = data['_id']
        del data['_id']
        return cls.init_with_dict(data)

    def encode_for_mongo(self):
        node = asdict(self)
        node['_id'] = node['remote_host']
        del node['remote_host']

# Path is /remote-node as per Team 10's documentation
@router.get('/remote-node',
    description='Validate node',
    responses={
                200: {'model': NodeAuthenticated},
                401: {'model': NodeValidationFail},
                404: {'model': NodeValidationFail},
              })
async def validate_node(response: Response,
                        origin: str | None = Header(default=None),
                        credentials: HTTPBasicCredentials = Depends(security)):
    db = SocialDatabase().database
    try:
        if not origin:
            raise AttributeError

        node = db.nodes.find_one({'_id': origin})
        if not node:
            raise AttributeError

    except AttributeError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'message': 'Node not found'}

    # Check credentials and return expected response
    node = Node.init_from_mongo(node)
    if compare_digest(node.remote_username, credentials.username)\
        and compare_digest(node.remote_password, credentials.password):
        return {'message': 'Authentication passed!', 'type': 'remoteNode'}

    response.status_code = status.HTTP_404_NOT_FOUND
    return {'message': 'Unauthorized credentials'}
