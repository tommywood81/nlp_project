from __future__ import annotations

from typing import List
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.news_feed import fetch_abc_feed
from app.models.sentiment import SentimentStrategy
from app.models.ner import NERStrategy
from app.models.summarize import SummarizationStrategy
from app.models.emotion import EmotionStrategy
from app.models.qa import QAStrategy

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


@router.get("/analyze", response_class=HTMLResponse)
async def analyze_article(
    request: Request,
    feed_name: str = Query("top_stories"),
    index: int = Query(0),
    tools: str = Query("sentiment"),
    question: str | None = Query(None),
):
    try:
        articles = fetch_abc_feed(feed_name=feed_name, full_text=True)
        article = articles[index]
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid article selection: {exc}")

    tool_list: List[str] = [t.strip() for t in tools.split(",") if t.strip()]
    outputs = {}

    # Build strategies lazily
    strategies = {
        "sentiment": SentimentStrategy(),
        "ner": NERStrategy(),
        "summarize": SummarizationStrategy(),
        "emotion": EmotionStrategy(),
        "qa": QAStrategy(),
    }

    text = article.full_text or article.summary

    for t in tool_list:
        if t == "qa":
            # Handle QA after the loop so we can provide a default/fallback question
            continue
        strat = strategies.get(t)
        if strat is None:
            continue
        outputs[t] = strat.analyze(text=text)

    if "qa" in tool_list:
        qa_question = (question or "What is the main point of this article?").strip()
        outputs["qa"] = strategies["qa"].analyze(text=qa_question, context=text)

    return templates.TemplateResponse(
        "news_result.html",
        {
            "request": request,
            "article": article,
            "tools": tool_list,
            "outputs": outputs,
        },
    )
