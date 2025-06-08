import spacy
from .base_strategy import NLPStrategy

nlp_model = spacy.load("en_core_web_sm")

class NERStrategy(NLPStrategy):
    def analyze(self, text: str, **kwargs):
        doc = nlp_model(text)
        return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]