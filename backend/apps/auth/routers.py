from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
import uuid

import json
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError

router = APIRouter()

config = Config('.env')
oauth = OAuth(config)

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Login Route
@router.get('/login', tags=['authentication'])
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

# Handle authentication callback
@router.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    
    user = token.get('userinfo')
    
    if user:
        # Save to database
        employee = {
            "_id": str(uuid.uuid4()),
            "email": user.email,
            "firstname": user.given_name,
            "lastname": user.family_name,
        }
        document = jsonable_encoder(employee)
        
        if (await request.app.mongodb["employees"].find_one({"email": user.email})) is None:
            await request.app.mongodb["employees"].insert_one(document)
        
        request.session['user'] = dict(user)
    return RedirectResponse(url='/')

# Logout Route
@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')