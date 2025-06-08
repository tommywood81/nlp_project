from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.models.sentiment import SentimentStrategy
from app.models.ner import NERStrategy
from app.models.summarize import SummarizationStrategy
from app.models.emotion import EmotionStrategy
from app.models.qa import QAStrategy

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

example_texts = {
    "sentiment": [
        "I love this product! It works perfectly.",
        "This is the worst experience I've ever had.",
        "I'm not sure how I feel about this.",
        "Absolutely fantastic service!",
        "The food was cold and tasteless.",
        "It's okay, nothing special.",
        "I'm so happy with my results!",
        "I wouldn't recommend this to anyone.",
        "It's just average, not good or bad.",
        "This made my day!"
    ],
    "ner": [
        "Barack Obama was born in Hawaii.",
        "Apple released the new iPhone in California.",
        "The Eiffel Tower is in Paris.",
        "Amazon is hiring in Seattle.",
        "Elon Musk founded SpaceX.",
        "The Olympics will be held in Tokyo.",
        "Google's headquarters are in Mountain View.",
        "The Mona Lisa is displayed in the Louvre.",
        "Mount Everest is the tallest mountain.",
        "Tesla cars are popular in Europe."
    ],
    "summarize": [
        "Artificial intelligence is transforming industries by automating tasks, improving efficiency, and enabling new capabilities that were previously impossible.",
        "The quick brown fox jumps over the lazy dog. This sentence contains every letter in the English alphabet and is often used for typing practice.",
        "Climate change is a global challenge that requires urgent action from governments, businesses, and individuals to reduce carbon emissions and protect the environment.",
        "The history of the internet dates back to the 1960s, evolving from a military project to the global network we use today.",
        "Renewable energy sources like solar and wind are becoming more affordable and widespread, helping to reduce reliance on fossil fuels.",
        "The novel tells the story of a young girl who overcomes adversity through courage and determination.",
        "Vaccines have played a crucial role in eradicating diseases and improving public health worldwide.",
        "The company reported record profits this quarter, driven by strong sales and innovative new products.",
        "Space exploration has led to numerous technological advancements that benefit everyday life.",
        "Exercise and a balanced diet are essential for maintaining good health and preventing chronic diseases."
    ],
    "emotion": [
        "I am so excited for my birthday party!",
        "This news makes me really sad.",
        "I'm furious about what happened yesterday.",
        "I feel calm and relaxed by the ocean.",
        "That movie was hilarious, I couldn't stop laughing!",
        "I'm terrified of spiders.",
        "I feel grateful for my friends and family.",
        "I'm anxious about the upcoming exam.",
        "Winning the award filled me with pride.",
        "I'm disappointed with the results."
    ],
    "qa": [
        "What is the capital of France?||Paris is the capital and most populous city of France.",
        "Who wrote Hamlet?||Hamlet is a tragedy written by William Shakespeare sometime between 1599 and 1601.",
        "What is the boiling point of water?||Water boils at 100 degrees Celsius at standard atmospheric pressure.",
        "Who painted the Mona Lisa?||The Mona Lisa was painted by Leonardo da Vinci in the early 16th century.",
        "What is the largest planet in our solar system?||Jupiter is the largest planet in our solar system.",
        "Who discovered penicillin?||Penicillin was discovered by Alexander Fleming in 1928.",
        "What is the tallest mountain in the world?||Mount Everest is the tallest mountain in the world.",
        "Who is the CEO of Tesla?||Elon Musk is the CEO of Tesla, Inc.",
        "What is the chemical symbol for gold?||The chemical symbol for gold is Au.",
        "What year did the first man land on the moon?||Neil Armstrong landed on the moon in 1969."
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
    return templates.TemplateResponse("index.html", {"request": request, "example_texts": example_texts[task], "task": task})

@router.post("/analyze/{task}", response_class=HTMLResponse)
def analyze(request: Request, task: str, text: str = Form(...), context: str = Form("")):
    if task == "qa" and (not text.strip() or not context.strip()):
        error_msg = "Both question and context are required for QA. Please provide both."
        return templates.TemplateResponse("result.html", {"request": request, "result": error_msg, "task": task})
    result = strategies[task].analyze(text=text, context=context)
    return templates.TemplateResponse("result.html", {"request": request, "result": result, "task": task})