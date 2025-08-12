# NLP Portfolio Dashboard

A comprehensive Natural Language Processing dashboard that demonstrates real-world NLP applications using modern AI models. Built with FastAPI and featuring live news analysis, this project showcases practical implementations of sentiment analysis, entity recognition, text summarization, emotion detection, and question answering.

## 🎯 What This Project Does

This dashboard lets you analyze text in multiple ways using state-of-the-art NLP models. You can either input your own text or analyze live news articles from ABC News Australia. It's designed to be both a portfolio piece and a practical tool for understanding how different NLP techniques work in real-world scenarios.

## 🚀 Live Demo

**Production URL**: http://209.38.89.159:8001

The dashboard is deployed on a Digital Ocean droplet and features:
- Real-time news analysis from ABC News Australia
- Interactive text processing with immediate results
- Detailed model information and accuracy metrics
- Professional, responsive UI

## 🧠 NLP Models & Capabilities

### Sentiment Analysis
- **Model**: TextBlob (PatternAnalyzer)
- **Accuracy**: ~60-70% on movie reviews
- **What it does**: Analyzes text tone and objectivity
- **Output**: Polarity score (-1 to 1) and subjectivity score (0 to 1)
- **Best for**: Quick sentiment checks, prototyping, educational purposes

### Named Entity Recognition (NER)
- **Model**: spaCy en_core_web_sm
- **Accuracy**: ~85% F-score on CoNLL-2003 dataset
- **What it does**: Identifies people, organizations, locations, and other entities
- **Output**: Tagged entities with confidence scores
- **Best for**: Information extraction, data mining, content analysis

### Text Summarization
- **Model**: HuggingFace T5-small
- **Accuracy**: ROUGE-2 F1 ~18-20 on CNN/DailyMail
- **What it does**: Condenses long text into concise summaries
- **Output**: Shorter, readable version of input text
- **Best for**: Article summarization, content condensation, research

### Emotion Detection
- **Model**: bhadresh-savani/distilbert-base-uncased-emotion
- **Accuracy**: ~91% on GoEmotions dataset
- **What it does**: Classifies text into specific emotions
- **Output**: Emotion labels with confidence scores
- **Best for**: Social media analysis, customer feedback, sentiment analysis

### Question Answering
- **Model**: distilbert/distilbert-base-cased-distilled-squad
- **Accuracy**: EM: 79.1, F1: 86.9 on SQuAD v1.1
- **What it does**: Answers questions based on provided context
- **Output**: Answer span with confidence score
- **Best for**: Information retrieval, chatbots, document Q&A

## 🏗️ Architecture & Pipeline

### Backend Structure
```
app/
├── config.py           # App configuration and settings
├── main.py            # FastAPI app initialization
├── models/            # NLP model implementations
│   ├── base_strategy.py
│   ├── sentiment.py
│   ├── ner.py
│   ├── summarize.py
│   ├── emotion.py
│   └── qa.py
├── routers/           # API route handlers
│   ├── home.py        # Landing page
│   ├── nlp.py         # Analysis endpoints
│   └── news.py        # News feed handling
├── services/          # Business logic
│   └── news_feed.py   # ABC News RSS integration
├── static/            # CSS and assets
└── templates/         # HTML templates
```

### Data Flow Pipeline
1. **Input**: User provides text or selects news article
2. **Processing**: Text is sent to appropriate NLP model
3. **Analysis**: Model processes text and returns structured results
4. **Display**: Results are formatted and displayed with model information
5. **Caching**: News feeds are cached for 10 minutes to reduce API calls

### News Integration
- **Source**: ABC News Australia RSS feeds
- **Feeds**: Top stories, world news, technology, business
- **Processing**: Full article extraction using newspaper3k
- **Caching**: 10-minute TTL to minimize external API calls

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11
- **NLP Libraries**: TextBlob, spaCy, HuggingFace Transformers
- **Frontend**: Jinja2 templates, vanilla CSS/JS
- **Data Processing**: newspaper3k, feedparser
- **Deployment**: Docker, Digital Ocean
- **Architecture**: Service-oriented, modular design

## 🚀 Quick Start

### Local Development
```bash
# Clone the repository
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

Visit `http://127.0.0.1:8000/home` to start using the dashboard.

### Docker Deployment
```bash
# Build and run with Docker
docker build -t nlp-dashboard .
docker run -p 8001:8000 nlp-dashboard

# Or use the deployment scripts
python push_to_dockerhub.py      # Build and push to Docker Hub
python deploy_droplet.py         # Deploy to Digital Ocean droplet
```

## 🎯 Use Cases & Applications

### Portfolio Demonstration
- Showcase NLP expertise with real-world applications
- Demonstrate understanding of different model types and their trade-offs
- Present results in a professional, accessible format

### News Analysis
- Analyze current events using live news feeds
- Track sentiment trends in news coverage
- Extract key entities and topics from articles

### Educational Tool
- Learn about different NLP techniques
- Compare model accuracies and use cases
- Understand the practical applications of AI models

### Research & Development
- Test NLP models on real-world data
- Prototype new analysis pipelines
- Benchmark different approaches

## 📊 Performance & Optimization

- **Caching Strategy**: News feeds cached for 10 minutes
- **Async Processing**: Non-blocking news feed fetching
- **Error Handling**: Graceful degradation for external failures
- **Responsive Design**: Mobile-friendly interface
- **Model Loading**: Lazy loading of heavy models

## 🔧 Configuration

Environment variables (optional):
```bash
ABC_NEWS_FEED_URLS=your_custom_feeds
NEWS_CACHE_TTL_MINUTES=10
HTTP_REQUEST_TIMEOUT_SECONDS=30
```

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

Tests cover:
- Individual model functionality
- Integration testing
- News feed service
- Error handling

## 🚀 Deployment

The project includes comprehensive deployment scripts:

- **Local Docker**: `deploy_local_docker_hub.py`
- **Cloud Deployment**: `deploy_droplet.py`
- **Complete Workflow**: `deploy_workflow.py`
- **Docker Hub Push**: `push_to_dockerhub.py`

## 📈 Future Enhancements

- Additional NLP models (translation, text generation)
- Real-time streaming analysis
- User authentication and saved analyses
- API endpoints for external integration
- Advanced visualization of results

## 🤝 Contributing

This is a portfolio project, but feel free to fork and adapt for your own use. The modular architecture makes it easy to add new models or features.

## 📝 License

MIT License - use this project for your portfolio, learning, or commercial applications.

---

*Built with modern Python web development practices and a focus on practical NLP applications.*