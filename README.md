# NLP Portfolio Dashboard

A production-ready Natural Language Processing dashboard built with FastAPI, featuring real-time news analysis and comprehensive text processing capabilities.

## 🚀 Features

- **Multi-Model NLP Pipeline**: Sentiment analysis, Named Entity Recognition, text summarization, emotion detection, and question answering
- **Live News Integration**: Real-time ABC News Australia RSS feed analysis
- **Professional UI**: Clean, responsive SaaS-style interface with intuitive navigation
- **Production Architecture**: Modular design with proper separation of concerns, caching, and error handling

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11
- **NLP Models**: TextBlob, spaCy, HuggingFace Transformers (T5, DistilBERT)
- **Frontend**: Jinja2 templates, CSS3, vanilla JavaScript
- **Data Sources**: ABC News RSS feeds, newspaper3k for article extraction
- **Architecture**: Service-oriented design with Pydantic validation

## 📊 NLP Capabilities

| Model | Technology | Use Case |
|-------|------------|----------|
| **Sentiment Analysis** | TextBlob | Polarity & subjectivity scoring |
| **Named Entity Recognition** | spaCy en_core_web_sm | Person, organization, location extraction |
| **Text Summarization** | T5-small | Concise article summaries |
| **Emotion Detection** | DistilBERT | Multi-label emotion classification |
| **Question Answering** | DistilBERT-SQuAD | Context-based Q&A |

## 🏃‍♂️ Quick Start

```bash
# Clone and setup
git clone https://github.com/tommywood81/nlp_project.git
cd nlp_project

# Create virtual environment
python -m venv env
.\env\Scripts\Activate.ps1  # Windows
source env/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Visit `http://127.0.0.1:8000/home` to explore the dashboard.

## 🎯 Use Cases

- **Portfolio Demonstration**: Showcase NLP expertise with real-world applications
- **News Analysis**: Analyze current events using live ABC News feeds
- **Text Processing**: Process custom text through multiple NLP pipelines
- **Educational Tool**: Learn about different NLP techniques and their applications

## 🏗️ Architecture

```
app/
├── config/          # Application settings & configuration
├── models/          # NLP strategy implementations
├── routers/         # FastAPI route handlers
├── services/        # Business logic (news feed, caching)
├── static/          # CSS, JavaScript assets
└── templates/       # Jinja2 HTML templates
```

## 📈 Performance

- **Caching**: 10-minute TTL for RSS feeds to reduce API calls
- **Async Processing**: Non-blocking news feed fetching
- **Error Handling**: Graceful degradation for external service failures
- **Responsive Design**: Mobile-friendly interface

## 🔧 Configuration

Environment variables (optional):
- `ABC_NEWS_FEED_URLS`: Custom RSS feed URLs
- `NEWS_CACHE_TTL_MINUTES`: Cache duration
- `HTTP_REQUEST_TIMEOUT_SECONDS`: Network timeout

## 📝 License

MIT License - feel free to use this project for your own portfolio or learning purposes.

---

*Built with ❤️ using modern Python web development practices*