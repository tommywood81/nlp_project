from transformers import pipeline
from .base_strategy import NLPStrategy

summarizer = pipeline("summarization", model="t5-small")

class SummarizationStrategy(NLPStrategy):
    def analyze(self, text: str, **kwargs):
        summary = summarizer(text, max_length=60, min_length=10, do_sample=False)
        return {"summary": summary[0]["summary_text"]}