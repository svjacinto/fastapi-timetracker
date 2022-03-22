import uvicorn
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from config import settings
from apps.auth.routers import router as auth_router
from apps.timerecords.routers import router as timerecord_router
from apps.employees.routers import router as employee_router

import json
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="secret-string")

# Homepage Route
@app.get('/')
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        data = json.dumps(user)
        html = (
            f'<pre>{data}</pre>'
            '<a href="/auth/logout">logout</a>'
        )
        return HTMLResponse(html)
    return HTMLResponse('<a href="/auth/login">login</a>')

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
app.include_router(auth_router, tags=["auth"], prefix="/auth")
app.include_router(timerecord_router, tags=["timerecords"], prefix="/api/timerecords")
app.include_router(employee_router, tags=["employees"], prefix="/api/employees")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host = settings.HOST,
        reload = settings.DEBUG_MODE,
        port = settings.PORT,
    )

   