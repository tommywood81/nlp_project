# NLP Dashboard Tutorial: From Concept to Production

This tutorial walks through building a production-ready NLP dashboard using FastAPI, covering everything from basic setup to advanced features like live news integration and caching.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Setup & Installation](#setup--installation)
3. [Core Architecture](#core-architecture)
4. [NLP Models Deep Dive](#nlp-models-deep-dive)
5. [FastAPI Router System](#fastapi-router-system)
6. [News Integration Pipeline](#news-integration-pipeline)
7. [Frontend & UI](#frontend--ui)
8. [Production Features](#production-features)
9. [Testing & Deployment](#testing--deployment)

---

## Project Overview

Our NLP dashboard demonstrates modern web development practices while showcasing five different NLP techniques. The application allows users to:
- Analyze custom text using multiple NLP models
- Process live news articles from ABC News Australia
- Run full pipeline analysis on any text
- Get detailed explanations of each model's capabilities

### Key Technologies
- **Backend**: FastAPI (async, type-safe, auto-documentation)
- **NLP**: TextBlob, spaCy, HuggingFace Transformers
- **Frontend**: Jinja2 templates with modern CSS
- **Data**: RSS feeds with newspaper3k for article extraction

---

## Setup & Installation

### 1. Environment Setup

```bash
# Create project structure
mkdir nlp_project
cd nlp_project

# Create virtual environment
python -m venv env
.\env\Scripts\Activate.ps1  # Windows
source env/bin/activate     # Linux/Mac

# Install core dependencies
pip install fastapi uvicorn jinja2 python-multipart
```

### 2. Project Structure

```
nlp_project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Settings and configuration
│   ├── models/              # NLP model implementations
│   │   ├── __init__.py
│   │   ├── base_strategy.py # Abstract base class
│   │   ├── sentiment.py     # Sentiment analysis
│   │   ├── ner.py          # Named Entity Recognition
│   │   ├── summarize.py    # Text summarization
│   │   ├── emotion.py      # Emotion detection
│   │   └── qa.py           # Question answering
│   ├── routers/            # FastAPI route handlers
│   │   ├── __init__.py
│   │   ├── nlp.py          # Main NLP analysis routes
│   │   ├── news.py         # News feed routes
│   │   └── home.py         # Landing page routes
│   ├── services/           # Business logic
│   │   ├── __init__.py
│   │   └── news_feed.py    # RSS feed service
│   ├── static/             # CSS, JS assets
│   │   └── style.css
│   └── templates/          # HTML templates
│       ├── index.html      # Main analysis page
│       ├── result.html     # Results display
│       ├── landing.html    # Home page
│       ├── news.html       # News browser
│       └── news_result.html # News analysis results
├── tests/                  # Unit tests
├── requirements.txt        # Dependencies
└── README.md              # Project documentation
```

### 3. Core Dependencies

```python
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
jinja2==3.1.2
python-multipart==0.0.6
textblob==0.17.1
spacy==3.7.2
transformers==4.35.2
torch==2.1.1
feedparser==6.0.10
newspaper3k==0.2.8
requests==2.31.0
pydantic-settings==2.1.0
lxml==4.9.3
lxml_html_clean==0.1.0
```

---

## Core Architecture

### 1. FastAPI Application Entry Point

```python
# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import settings
from app.routers import nlp as nlp_router
from app.routers import news as news_router
from app.routers import home as home_router

app = FastAPI(title="NLP Portfolio Dashboard")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(nlp_router.router, prefix="/analyze")
app.include_router(news_router.router, prefix="/news")
app.include_router(home_router.router)

# Templates
templates = Jinja2Templates(directory="app/templates")
```

### 2. Configuration Management

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, Field
from datetime import timedelta

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    app_name: str = "NLP Portfolio API"
    
    # RSS feed URLs
    abc_news_feed_urls: dict[str, AnyHttpUrl] = {
        "top_stories": "https://www.abc.net.au/news/feed/51120/rss.xml",
        "australia": "https://www.abc.net.au/news/feed/51892/rss.xml",
        "just_in": "https://www.abc.net.au/news/feed/52498/rss.xml",
    }
    
    # Performance settings
    news_cache_ttl_minutes: int = 10
    http_request_timeout_seconds: int = 10

settings = Settings()
```

### 3. Strategy Pattern for NLP Models

```python
# app/models/base_strategy.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseStrategy(ABC):
    """Abstract base class for all NLP strategies"""
    
    @abstractmethod
    def analyze(self, text: str, **kwargs) -> Dict[str, Any]:
        """Analyze text and return results"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this strategy"""
        pass
```

---

## NLP Models Deep Dive

### 1. Sentiment Analysis (TextBlob)

**What it does**: Analyzes the emotional tone and subjectivity of text.

```python
# app/models/sentiment.py
from textblob import TextBlob
from app.models.base_strategy import BaseStrategy

class SentimentStrategy(BaseStrategy):
    def analyze(self, text: str, **kwargs) -> Dict[str, Any]:
        blob = TextBlob(text)
        
        return {
            "polarity": blob.sentiment.polarity,  # -1 to 1 (negative to positive)
            "subjectivity": blob.sentiment.subjectivity,  # 0 to 1 (objective to subjective)
            "interpretation": self._interpret_sentiment(blob.sentiment.polarity)
        }
    
    def _interpret_sentiment(self, polarity: float) -> str:
        if polarity > 0.1:
            return "Positive"
        elif polarity < -0.1:
            return "Negative"
        else:
            return "Neutral"
    
    @property
    def name(self) -> str:
        return "Sentiment Analysis"
```

**How it works**: TextBlob uses a lexicon-based approach, counting positive and negative words to determine sentiment polarity and subjectivity.

### 2. Named Entity Recognition (spaCy)

**What it does**: Identifies and classifies named entities (people, organizations, locations, etc.).

```python
# app/models/ner.py
import spacy
from app.models.base_strategy import BaseStrategy
from typing import Dict, Any

class NERStrategy(BaseStrategy):
    def __init__(self):
        # Load spaCy model (download with: python -m spacy download en_core_web_sm)
        self.nlp = spacy.load("en_core_web_sm")
    
    def analyze(self, text: str, **kwargs) -> Dict[str, Any]:
        doc = self.nlp(text)
        
        entities = {}
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append({
                "text": ent.text,
                "start": ent.start_char,
                "end": ent.end_char
            })
        
        return {
            "entities": entities,
            "entity_count": len(doc.ents),
            "entity_types": list(entities.keys())
        }
    
    @property
    def name(self) -> str:
        return "Named Entity Recognition"
```

**Entity Types**: PERSON, ORG, GPE (countries/cities), DATE, MONEY, etc.

### 3. Text Summarization (T5)

**What it does**: Creates concise summaries of longer text passages.

```python
# app/models/summarize.py
from transformers import pipeline
from app.models.base_strategy import BaseStrategy

class SummarizeStrategy(BaseStrategy):
    def __init__(self):
        # Load T5-small model for summarization
        self.summarizer = pipeline(
            "summarization",
            model="t5-small",
            tokenizer="t5-small"
        )
    
    def analyze(self, text: str, **kwargs) -> Dict[str, Any]:
        # T5 works best with longer texts
        if len(text.split()) < 50:
            return {"summary": text, "note": "Text too short for meaningful summarization"}
        
        # Generate summary
        result = self.summarizer(
            text,
            max_length=150,
            min_length=30,
            do_sample=False
        )
        
        return {
            "summary": result[0]["summary_text"],
            "original_length": len(text.split()),
            "summary_length": len(result[0]["summary_text"].split())
        }
    
    @property
    def name(self) -> str:
        return "Text Summarization"
```

**How T5 works**: Uses a transformer architecture trained on text-to-text tasks, converting input text to a shorter summary.

### 4. Emotion Detection (DistilBERT)

**What it does**: Classifies text into multiple emotion categories.

```python
# app/models/emotion.py
from transformers import pipeline
from app.models.base_strategy import BaseStrategy

class EmotionStrategy(BaseStrategy):
    def __init__(self):
        # Load emotion classification model
        self.classifier = pipeline(
            "text-classification",
            model="bhadresh-savani/distilbert-base-uncased-emotion",
            return_all_scores=True
        )
    
    def analyze(self, text: str, **kwargs) -> Dict[str, Any]:
        results = self.classifier(text)
        
        # Get top emotions
        emotions = results[0]
        top_emotion = max(emotions, key=lambda x: x["score"])
        
        return {
            "emotions": emotions,
            "primary_emotion": top_emotion["label"],
            "confidence": top_emotion["score"],
            "all_scores": {e["label"]: e["score"] for e in emotions}
        }
    
    @property
    def name(self) -> str:
        return "Emotion Detection"
```

**Emotion Categories**: joy, sadness, anger, fear, surprise, love, neutral.

### 5. Question Answering (DistilBERT-SQuAD)

**What it does**: Answers questions based on provided context.

```python
# app/models/qa.py
from transformers import pipeline
from app.models.base_strategy import BaseStrategy

class QAStrategy(BaseStrategy):
    def __init__(self):
        # Load QA model trained on SQuAD dataset
        self.qa_pipeline = pipeline(
            "question-answering",
            model="distilbert/distilbert-base-cased-distilled-squad"
        )
    
    def analyze(self, text: str, context: str = None, **kwargs) -> Dict[str, Any]:
        if not context:
            return {"error": "Context required for question answering"}
        
        result = self.qa_pipeline(
            question=text,
            context=context
        )
        
        return {
            "answer": result["answer"],
            "confidence": result["score"],
            "start": result["start"],
            "end": result["end"]
        }
    
    @property
    def name(self) -> str:
        return "Question Answering"
```

**How it works**: Uses a transformer model to find the most relevant text span in the context that answers the question.

---

## FastAPI Router System

### 1. Main NLP Router

```python
# app/routers/nlp.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.models import sentiment, ner, summarize, emotion, qa

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Strategy mapping
strategies = {
    "sentiment": sentiment.SentimentStrategy(),
    "ner": ner.NERStrategy(),
    "summarize": summarize.SummarizeStrategy(),
    "emotion": emotion.EmotionStrategy(),
    "qa": qa.QAStrategy()
}

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, task: str = "sentiment"):
    """Main analysis page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "task": task}
    )

@router.post("/{task}", response_class=HTMLResponse)
async def analyze_text(
    request: Request,
    task: str,
    text: str = Form(...),
    context: str = Form(None)
):
    """Analyze text using specified NLP model"""
    
    strategy = strategies.get(task)
    if not strategy:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": f"Unknown task: {task}"}
        )
    
    try:
        # Handle QA specially (needs context)
        if task == "qa":
            result = strategy.analyze(text=text, context=context)
        else:
            result = strategy.analyze(text=text)
        
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "task": task,
                "result": result,
                "input_text": text
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)}
        )
```

### 2. News Router

```python
# app/routers/news.py
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.news_feed import fetch_abc_feed
from app.models import sentiment, ner, summarize, emotion, qa

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/browse", response_class=HTMLResponse)
async def browse_news(
    request: Request,
    feed_name: str = Query("top_stories")
):
    """Browse ABC News articles"""
    try:
        articles = fetch_abc_feed(feed_name)
        return templates.TemplateResponse(
            "news.html",
            {
                "request": request,
                "articles": articles,
                "feed_name": feed_name
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)}
        )

@router.get("/analyze", response_class=HTMLResponse)
async def analyze_article(
    request: Request,
    feed_name: str = Query("top_stories"),
    index: int = Query(0),
    tools: str = Query("sentiment"),
    question: str = Query(None)
):
    """Analyze a specific news article"""
    
    # Fetch article
    articles = fetch_abc_feed(feed_name)
    if index >= len(articles):
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Article not found"}
        )
    
    article = articles[index]
    text = article.full_text or article.summary
    
    # Parse tools
    tool_list = [t.strip() for t in tools.split(",")]
    outputs = {}
    
    # Run analysis
    for tool in tool_list:
        if tool == "qa" and question:
            outputs[tool] = qa.QAStrategy().analyze(
                text=question, 
                context=text
            )
        elif tool in ["sentiment", "ner", "summarize", "emotion"]:
            strategy = strategies.get(tool)
            if strategy:
                outputs[tool] = strategy.analyze(text=text)
    
    return templates.TemplateResponse(
        "news_result.html",
        {
            "request": request,
            "article": article,
            "outputs": outputs
        }
    )
```

---

## News Integration Pipeline

### 1. RSS Feed Service

```python
# app/services/news_feed.py
import feedparser
import requests
from newspaper import Article
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, AnyHttpUrl
from app.config import settings

class NewsArticle(BaseModel):
    title: str
    link: AnyHttpUrl
    published: Optional[str] = None
    summary: Optional[str] = None
    full_text: Optional[str] = None

# Simple in-memory cache
_cache_data: Optional[List[NewsArticle]] = None
_cache_expiry: Optional[datetime] = None

def fetch_abc_feed(feed_name: str = "top_stories", full_text: bool = False) -> List[NewsArticle]:
    """Fetch and cache ABC News RSS feed"""
    global _cache_data, _cache_expiry
    
    # Check cache
    if _cache_data and _cache_expiry and _cache_expiry > datetime.utcnow():
        return _cache_data
    
    # Fetch from RSS
    feed_url = settings.abc_news_feed_urls.get(feed_name)
    if not feed_url:
        raise ValueError(f"Invalid feed name: {feed_name}")
    
    try:
        feed = feedparser.parse(feed_url)
        articles = []
        
        for entry in feed.entries:
            article_data = {
                "title": entry.title,
                "link": entry.link,
                "published": entry.get("published", ""),
                "summary": entry.get("summary", "")
            }
            
            # Optionally fetch full text
            if full_text:
                try:
                    article = Article(entry.link)
                    article.download()
                    article.parse()
                    article_data["full_text"] = article.text
                except Exception:
                    article_data["full_text"] = None
            
            articles.append(NewsArticle(**article_data))
        
        # Update cache
        _cache_data = articles
        _cache_expiry = datetime.utcnow() + timedelta(
            minutes=settings.news_cache_ttl_minutes
        )
        
        return articles
        
    except requests.RequestException as e:
        raise RuntimeError(f"Error fetching RSS feed: {e}")
```

### 2. Caching Strategy

The news service implements a simple TTL (Time-To-Live) cache to:
- Reduce API calls to ABC News
- Improve response times
- Handle rate limiting gracefully

**Cache Configuration**:
- TTL: 10 minutes (configurable)
- Storage: In-memory (simple but effective for demo)
- Invalidation: Automatic based on expiry time

---

## Frontend & UI

### 1. Template Structure

```html
<!-- app/templates/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Analyse Your Own Text</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <header class="page-header">
        <div class="container">
            <h1>Analyse Your Own Text</h1>
            <p class="subtitle">Paste your text and explore Sentiment, NER, Summarisation, Emotion, or QA.</p>
        </div>
    </header>

    <section class="container">
        <!-- Tool Selection Navigation -->
        <nav style="margin-bottom: 1rem; display:flex; gap:0.5rem; flex-wrap:wrap;">
            <a href="/?task=sentiment" class="button-secondary{% if task == 'sentiment' or not task %} active{% endif %}">Sentiment</a>
            <a href="/?task=ner" class="button-secondary{% if task == 'ner' %} active{% endif %}">NER</a>
            <a href="/?task=summarize" class="button-secondary{% if task == 'summarize' %} active{% endif %}">Summarise</a>
            <a href="/?task=emotion" class="button-secondary{% if task == 'emotion' %} active{% endif %}">Emotion</a>
            <a href="/?task=qa" class="button-secondary{% if task == 'qa' %} active{% endif %}">QA</a>
        </nav>

        <!-- Analysis Form -->
        <form id="nlp-form" action="/analyze/{{ task | default('sentiment') }}" method="post" class="analysis-form">
            <!-- Dynamic form based on selected tool -->
            {% if task == "qa" %}
                <label>Question</label>
                <textarea name="text" rows="2" placeholder="Ask your question..."></textarea>
                <label>Context</label>
                <textarea name="context" rows="4" placeholder="Provide the context..."></textarea>
            {% else %}
                <label>Text to Analyze</label>
                <textarea name="text" rows="4" placeholder="Paste or type your text here..."></textarea>
            {% endif %}
            <button type="submit" class="button-primary">Run Analysis</button>
        </form>
    </section>
</body>
</html>
```

### 2. CSS Styling

```css
/* app/static/style.css */
body {
    font-family: 'Inter', Arial, sans-serif;
    margin: 0;
    padding: 0;
    background: #f9fafb;
    color: #111827;
}

.container {
    max-width: 900px;
    margin: auto;
    padding: 2rem;
}

.page-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 3rem 0;
    text-align: center;
}

.button-primary {
    background: #2563eb;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    text-decoration: none;
    font-weight: 600;
    border: none;
    cursor: pointer;
    transition: all 0.2s ease;
}

.button-primary:hover {
    background: #1d4ed8;
    transform: translateY(-1px);
}

.button-secondary {
    background: #f3f4f6;
    color: #374151;
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    text-decoration: none;
    font-weight: 600;
    border: 1px solid #d1d5db;
    transition: all 0.2s ease;
}

.button-secondary.active {
    background: #2563eb;
    color: white;
    border-color: #2563eb;
}

.results {
    background: #ffffff;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin-top: 1rem;
}
```

---

## Production Features

### 1. Error Handling

```python
# Global exception handler
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )
```

### 2. Input Validation

```python
from pydantic import BaseModel, validator

class AnalysisRequest(BaseModel):
    text: str
    context: str = None
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip()
    
    @validator('text')
    def text_must_be_reasonable_length(cls, v):
        if len(v) > 10000:
            raise ValueError('Text too long (max 10,000 characters)')
        return v
```

### 3. Performance Monitoring

```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

---

## Testing & Deployment

### 1. Unit Tests

```python
# tests/test_sentiment.py
import pytest
from app.models.sentiment import SentimentStrategy

def test_sentiment_positive():
    strategy = SentimentStrategy()
    result = strategy.analyze("I love this amazing product!")
    
    assert result["polarity"] > 0
    assert result["interpretation"] == "Positive"

def test_sentiment_negative():
    strategy = SentimentStrategy()
    result = strategy.analyze("This is terrible and awful.")
    
    assert result["polarity"] < 0
    assert result["interpretation"] == "Negative"

def test_sentiment_neutral():
    strategy = SentimentStrategy()
    result = strategy.analyze("The weather is cloudy today.")
    
    assert abs(result["polarity"]) < 0.1
    assert result["interpretation"] == "Neutral"
```

### 2. Integration Tests

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Analyse Your Own Text" in response.text

def test_sentiment_analysis():
    response = client.post(
        "/analyze/sentiment",
        data={"text": "I love this!"}
    )
    assert response.status_code == 200
    assert "Positive" in response.text

def test_news_browse():
    response = client.get("/news/browse")
    assert response.status_code == 200
    assert "ABC News" in response.text
```

### 3. Deployment

```bash
# Production deployment with Gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Docker deployment
docker build -t nlp-dashboard .
docker run -p 8000:8000 nlp-dashboard
```

---

## Advanced Features

### 1. Model Performance Comparison

```python
def compare_models(text: str) -> Dict[str, Any]:
    """Compare all models on the same text"""
    results = {}
    
    for name, strategy in strategies.items():
        try:
            start_time = time.time()
            result = strategy.analyze(text)
            end_time = time.time()
            
            results[name] = {
                "result": result,
                "processing_time": end_time - start_time,
                "success": True
            }
        except Exception as e:
            results[name] = {
                "error": str(e),
                "success": False
            }
    
    return results
```

### 2. Batch Processing

```python
async def batch_analyze(texts: List[str], task: str) -> List[Dict]:
    """Process multiple texts in parallel"""
    strategy = strategies.get(task)
    if not strategy:
        raise ValueError(f"Unknown task: {task}")
    
    # Process in batches to avoid memory issues
    batch_size = 10
    results = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_results = await asyncio.gather(
            *[analyze_single(strategy, text) for text in batch]
        )
        results.extend(batch_results)
    
    return results
```

---

## Conclusion

This tutorial covered building a complete NLP dashboard from scratch. Key takeaways:

1. **Modular Design**: Strategy pattern makes it easy to add new NLP models
2. **Production Ready**: Caching, error handling, and validation
3. **User Friendly**: Clean UI with intuitive navigation
4. **Scalable**: FastAPI's async capabilities handle concurrent requests
5. **Maintainable**: Clear separation of concerns and comprehensive testing

The project demonstrates modern Python web development practices while showcasing practical NLP applications. It's perfect for portfolios, learning, or as a foundation for more complex NLP applications.

---

*For more information, check out the [README.md](README.md) and explore the codebase!*
