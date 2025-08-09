from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.routers import nlp
from app.routers import news as news_router
from app.routers import home as home_router

app = FastAPI(title=settings.app_name)

app.include_router(home_router.router)
app.include_router(nlp.router)
app.include_router(news_router.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# terminate server with: taskkill /F /IM uvicorn.exe
# reload server with uvicorn app.main:app --reload
