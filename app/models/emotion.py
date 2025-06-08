from transformers import pipeline
from .base_strategy import NLPStrategy

emotion_pipeline = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", return_all_scores=False)

class EmotionStrategy(NLPStrategy):
    def analyze(self, text: str, **kwargs):
        return emotion_pipeline(text)[0]