from app.models.qa import QAStrategy

def test_qa():
    strategy = QAStrategy()
    question = "Where was Barack Obama born?"
    context = "Barack Obama was born in Hawaii."
    result = strategy.analyze(question, context=context)
    assert "answer" in result
    assert "score" in result
    assert isinstance(result["answer"], str)
    assert isinstance(result["score"], float) 