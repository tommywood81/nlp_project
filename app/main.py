from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routers import nlp

app = FastAPI(title="NLP Portfolio API")

app.include_router(nlp.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

#terminate server with: taskkill /F /IM uvicorn.exe
#reload server with uvicorn app.main:app --reload
