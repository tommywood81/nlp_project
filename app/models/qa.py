from transformers import pipeline
from .base_strategy import NLPStrategy
import logging

logger = logging.getLogger(__name__)

qa_pipeline = pipeline(
    "question-answering",
    model="distilbert/distilbert-base-cased-distilled-squad",
    revision="main"
)

class QAStrategy(NLPStrategy):
    def analyze(self, text: str, context: str, **kwargs):
        result = qa_pipeline(question=text, context=context)
        logger.info(f"QA input: question={text}, context={context}")
        logger.info(f"QA result: {result}")
        return {"answer": result.get("answer", ""), "score": result.get("score", 0.0)}