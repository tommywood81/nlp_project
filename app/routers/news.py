from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.news_feed import fetch_abc_feed

router = APIRouter(prefix="/news", tags=["news"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=JSONResponse)
async def get_news(feed_name: str = Query("top_stories"), full_text: bool = Query(False)):
    try:
        articles = fetch_abc_feed(feed_name=feed_name, full_text=full_text)
        return {"status": "success", "count": len(articles), "articles": [a.__dict__ for a in articles]}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=502, detail=f"Failed to fetch feed: {exc}")


@router.get("/browse", response_class=HTMLResponse)
async def browse_news(request: Request, feed_name: str = Query("top_stories")):
    try:
        articles = fetch_abc_feed(feed_name=feed_name, full_text=False)
    except Exception as exc:  # pragma: no cover
        articles = []
    return templates.TemplateResponse(
        "news.html",
        {"request": request, "articles": articles, "feed_name": feed_name},
    )
