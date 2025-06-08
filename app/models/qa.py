from transformers import pipeline
from .base_strategy import NLPStrategy

qa_pipeline = pipeline("question-answering")

class QAStrategy(NLPStrategy):
    def analyze(self, text: str, context: str, **kwargs):
        result = qa_pipeline(question=text, context=context)
        return {"answer": result["answer"], "score": result["score"]}