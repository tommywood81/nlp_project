import pytest
from app.models.ner import NERStrategy


def test_ner_entities():
    strategy = NERStrategy()
    text = "Barack Obama was born in Hawaii."
    result = strategy.analyze(text)
    entities = {ent["text"]: ent["label"] for ent in result}
    assert "Barack Obama" in entities
    assert entities["Barack Obama"] == "PERSON"
    assert "Hawaii" in entities
    assert entities["Hawaii"] == "GPE" 