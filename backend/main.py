
import uuid
import uvicorn
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient

from config import settings
from apps.timerecords.routers import router as timerecord_router
from apps.employees.routers import router as employee_router

import json
from starlette.config import Config
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError

app = FastAPI()

# Initialize our OAuth instance from the client ID and client secret specified in our .env file
app.add_middleware(SessionMiddleware, secret_key="secret-string")

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

# Homepage Route
@app.get('/')
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        data = json.dumps(user)
        html = (
            f'<pre>{data}</pre>'
            '<a href="/logout">logout</a>'
        )
        return HTMLResponse(html)
    return HTMLResponse('<a href="/login">login</a>')

# Login Route
@app.get('/login', tags=['authentication'])
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

# Handle authentication callback
@app.get('/auth')
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
@app.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

# @app.get("/")
# async def get_root():
#     return {"Message": "Hello World"}

# DATABASE
@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(settings.DB_URL)
    app.mongodb = app.mongodb_client[settings.DB_NAME]
    
@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
    
# ROUTERS
app.include_router(timerecord_router, tags=["timerecords"], prefix="/api/timerecords")
app.include_router(employee_router, tags=["employees"], prefix="/api/employees")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host = settings.HOST,
        reload = settings.DEBUG_MODE,
        port = settings.PORT,
    )

   