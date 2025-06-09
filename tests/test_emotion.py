from app.models.emotion import EmotionStrategy

def test_emotion():
    strategy = EmotionStrategy()
    text = "I am so happy today!"
    result = strategy.analyze(text)
    assert "label" in result
    assert "score" in result
    assert isinstance(result["label"], str)
    assert isinstance(result["score"], float) 