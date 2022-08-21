from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from .auth import get_current_user
from .routers import login, me, posts, users
from .settings import settings

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(
    posts.router, prefix="/posts", tags=["posts"], dependencies=[Depends(get_current_user)]
)
app.include_router(me.router, prefix="/me", tags=["me"])
app.include_router(login.router, prefix="/login", tags=["login"])


@app.get("/")
async def root():
    return {"message": "Hello World"}


register_tortoise(
    app=app,
    db_url=settings.DATABASE_URL,
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
