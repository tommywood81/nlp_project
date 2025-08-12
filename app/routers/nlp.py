from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.models.sentiment import SentimentStrategy
from app.models.ner import NERStrategy
from app.models.summarize import SummarizationStrategy
from app.models.emotion import EmotionStrategy
from app.models.qa import QAStrategy
from typing import List

try:
    # Optional import to avoid hard dependency at import time in tests
    from app.services.news_feed import fetch_abc_feed
except Exception:  # pragma: no cover
    fetch_abc_feed = None  # type: ignore

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

example_texts = {
    "sentiment": [
        "The ancient temple revealed its secrets with magnificent golden treasures!",
        "Beware the cursed chamber - it brings only death and despair.",
        "The archaeological discovery is neither remarkable nor disappointing.",
        "What an incredible find! The lost city of Atlantis awaits!",
        "The expedition was a complete disaster with no valuable artifacts.",
        "The ruins are interesting but not extraordinary.",
        "I'm thrilled to have discovered this ancient manuscript!",
        "This cursed tomb should never have been disturbed.",
        "The excavation yielded mixed results - some artifacts, some disappointment.",
        "The discovery of the Holy Grail fills me with joy!"
    ],
    "ner": [
        "Indiana Jones discovered the Ark of the Covenant in Tanis, Egypt.",
        "The Holy Grail was hidden in the Canyon of the Crescent Moon.",
        "Dr. Henry Jones Sr. was a professor at Marshall College.",
        "The Crystal Skull was found in the Amazon rainforest.",
        "Marion Ravenwood owned the Raven's Nest bar in Nepal.",
        "The Temple of Doom was located in Pankot Palace, India.",
        "Marcus Brody was the curator of the National Museum.",
        "Short Round helped Indiana escape from Shanghai.",
        "The Lost Ark was stored in a massive government warehouse.",
        "The Cross of Coronado was stolen from a museum in Utah."
    ],
    "summarize": [
        "Deep in the jungles of Peru, archaeologist Indiana Jones discovered an ancient temple complex that had remained hidden for centuries. The temple contained intricate hieroglyphics telling the story of a lost civilization that possessed advanced knowledge of astronomy and mathematics. Among the artifacts found were golden idols, ceremonial masks, and a mysterious crystal that seemed to glow with an otherworldly light. The discovery has sparked intense debate among scholars about the origins of this civilization and their connection to other ancient cultures. This find represents one of the most significant archaeological discoveries of the century.",
        "The ancient city of Petra, carved into the red sandstone cliffs of Jordan, stands as a testament to the ingenuity of the Nabataean people. This remarkable archaeological site features elaborate tombs, temples, and a sophisticated water system that allowed the city to thrive in the harsh desert environment. The Treasury, with its ornate facade and hidden chambers, has captured the imagination of explorers and archaeologists for generations. Recent excavations have revealed new insights into the city's trading networks and cultural connections with ancient Egypt, Greece, and Rome.",
        "The discovery of the Dead Sea Scrolls in the mid-20th century revolutionized our understanding of ancient Jewish texts and early Christianity. Found in caves near the Dead Sea, these ancient manuscripts include biblical texts, religious commentaries, and community rules dating back over 2,000 years. The scrolls provide invaluable insights into the religious and cultural practices of the time, offering scholars a window into the world of Second Temple Judaism. Their preservation in the arid climate of the Dead Sea region has allowed these fragile documents to survive for millennia.",
        "The Great Wall of China, stretching over 13,000 miles across northern China, represents one of the most ambitious construction projects in human history. Built over centuries by various Chinese dynasties, the wall served as both a defensive barrier and a symbol of imperial power. The construction techniques used, including the use of local materials and sophisticated engineering methods, demonstrate the advanced capabilities of ancient Chinese builders. Today, the wall stands as a UNESCO World Heritage site and continues to attract millions of visitors each year.",
        "The ancient Library of Alexandria, founded in the 3rd century BCE, was the greatest repository of knowledge in the ancient world. Housing hundreds of thousands of scrolls containing works from Greek, Egyptian, and other civilizations, the library served as a center of learning and scholarship. Scholars from across the Mediterranean world traveled to Alexandria to study and contribute to this vast collection of human knowledge. The library's destruction, whether by fire or gradual decline, represents one of the greatest losses of cultural heritage in history."
    ],
    "emotion": [
        "I'm absolutely thrilled to have discovered the lost temple!",
        "The ancient curse fills me with deep sorrow and regret.",
        "I'm absolutely furious that the artifact was stolen!",
        "The peaceful ruins bring me a sense of calm and wonder.",
        "The discovery of the golden idol made me laugh with joy!",
        "I'm terrified of the dark spirits that guard this tomb.",
        "I feel grateful for the ancient wisdom preserved in these texts.",
        "I'm anxious about what lies behind the sealed chamber door.",
        "Finding the Holy Grail fills me with immense pride and accomplishment.",
        "I'm disappointed that the treasure map led to an empty chamber."
    ],
    "qa": [
        "Where was the Ark of the Covenant discovered?||Indiana Jones discovered the Ark of the Covenant in the ancient city of Tanis, Egypt, buried deep beneath the desert sands.",
        "Who was Dr. Henry Jones Sr.?||Dr. Henry Jones Sr. was Indiana Jones's father, a professor of medieval literature who dedicated his life to finding the Holy Grail.",
        "What is the Holy Grail?||The Holy Grail is the legendary cup used by Jesus Christ at the Last Supper, said to grant eternal life to those who drink from it.",
        "Where was the Crystal Skull found?||The Crystal Skull was discovered in the depths of the Amazon rainforest, hidden within an ancient temple complex.",
        "Who is Marion Ravenwood?||Marion Ravenwood was Indiana Jones's former lover and the daughter of his mentor, who owned the Raven's Nest bar in Nepal.",
        "What is the Temple of Doom?||The Temple of Doom was an ancient temple located in Pankot Palace, India, where human sacrifices were performed to the goddess Kali.",
        "Who is Marcus Brody?||Marcus Brody was the curator of the National Museum and a close friend of Indiana Jones, often helping with archaeological expeditions.",
        "What is the Cross of Coronado?||The Cross of Coronado was a golden cross that belonged to Spanish conquistador Francisco Vásquez de Coronado, stolen from a museum in Utah.",
        "Where is the Lost Ark stored?||The Lost Ark is stored in a massive government warehouse, hidden away among countless other artifacts and treasures.",
        "What is the Canyon of the Crescent Moon?||The Canyon of the Crescent Moon is the location where the Holy Grail was hidden, accessible only through a series of deadly trials."
    ]
}

strategies = {
    "sentiment": SentimentStrategy(),
    "ner": NERStrategy(),
    "summarize": SummarizationStrategy(),
    "emotion": EmotionStrategy(),
    "qa": QAStrategy()
}

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    task = request.query_params.get("task", "sentiment")
    use_news = request.query_params.get("use_news", "0") == "1"
    feed_name = request.query_params.get("feed_name", "top_stories")

    news_articles = []
    if use_news and fetch_abc_feed is not None:
        try:
            news_articles = fetch_abc_feed(feed_name=feed_name, full_text=False)
        except Exception:
            news_articles = []

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "example_texts": example_texts[task],
            "task": task,
            "use_news": use_news,
            "feed_name": feed_name,
            "news_articles": news_articles,
        },
    )

@router.post("/analyze/{task}", response_class=HTMLResponse)
def analyze(request: Request, task: str, text: str = Form(...), context: str = Form("")):
    if task == "qa" and (not text.strip() or not context.strip()):
        error_msg = "Both question and context are required for QA. Please provide both."
        return templates.TemplateResponse("result.html", {"request": request, "result": error_msg, "task": task})
    
    result = strategies[task].analyze(text=text, context=context)
    
    # Add blurbs for explanation
    blurbs = {
        'sentiment': 'Reveals tone and objectivity; polarity in [-1,1], subjectivity in [0,1].',
        'ner': 'Finds entities like people, places, and organisations using token classification.',
        'summarize': 'Condenses long text into concise, readable summaries.',
        'emotion': 'Classifies nuanced emotions with per-class scores.',
        'qa': 'Extracts the most relevant answer span from the provided context.'
    }
    
    template_data = {
        "request": request, 
        "result": result, 
        "task": task,
        "blurbs": blurbs
    }
    
    # Add question and context for QA results
    if task == "qa":
        template_data["question"] = text
        template_data["context"] = context
    
    return templates.TemplateResponse("result.html", template_data)