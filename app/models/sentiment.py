from textblob import TextBlob
from .base_strategy import NLPStrategy

class SentimentStrategy(NLPStrategy):
    def analyze(self, text: str, **kwargs):
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        if polarity > 0.1:
            label = "positive"
        elif polarity < -0.1:
            label = "negative"
        else:
            label = "neutral"
        return {
            "sentiment": label,
            "polarity": polarity,
            "subjectivity": subjectivity
        }