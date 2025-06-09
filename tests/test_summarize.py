from app.models.summarize import SummarizationStrategy

def test_summarization():
    strategy = SummarizationStrategy()
    text = (
        "The Eiffel Tower is one of the most recognizable structures in the world. "
        "It was constructed in 1889 as the entrance arch to the 1889 World's Fair in Paris. "
        "Standing at 324 meters tall, it was the tallest man-made structure for 41 years. "
        "Today, it is a global cultural icon of France and a major tourist attraction, "
        "with millions of visitors every year."
    )
    result = strategy.analyze(text)
    summary = result["summary"]
    assert isinstance(summary, str)
    assert len(summary) < len(text) 