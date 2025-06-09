import pytest
from app.models.sentiment import SentimentStrategy

@pytest.mark.parametrize("text,expected_label", [
    ("I love this!", "positive"),
    ("I hate this!", "negative"),
    ("This is a book.", "neutral"),
])
def test_sentiment_labels(text, expected_label):
    strategy = SentimentStrategy()
    result = strategy.analyze(text)
    assert result["sentiment"] == expected_label
    assert isinstance(result["polarity"], float)
    assert isinstance(result["subjectivity"], float) 