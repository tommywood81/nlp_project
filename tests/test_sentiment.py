import pytest
from app.models.sentiment import SentimentStrategy

@pytest.mark.unit
class TestSentimentStrategy:
    """Test suite for SentimentStrategy"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.strategy = SentimentStrategy()
    
    @pytest.mark.parametrize("text,expected_sentiment", [
        ("I love this amazing product!", "positive"),
        ("This is absolutely wonderful!", "positive"),
        ("I hate this terrible product!", "negative"),
        ("This is awful and disgusting!", "negative"),
        ("This is a book.", "neutral"),
        ("The weather is cloudy today.", "neutral"),
    ])
    def test_sentiment_classification(self, text, expected_sentiment):
        """Test sentiment classification for various texts"""
        result = self.strategy.analyze(text)
        assert result["sentiment"] == expected_sentiment
        assert isinstance(result["polarity"], float)
        assert isinstance(result["subjectivity"], float)
    
    def test_polarity_range(self):
        """Test that polarity is within expected range [-1, 1]"""
        text = "I love this amazing product!"
        result = self.strategy.analyze(text)
        assert -1.0 <= result["polarity"] <= 1.0
    
    def test_subjectivity_range(self):
        """Test that subjectivity is within expected range [0, 1]"""
        text = "I think this is good."
        result = self.strategy.analyze(text)
        assert 0.0 <= result["subjectivity"] <= 1.0
    
    def test_empty_text(self):
        """Test handling of empty text"""
        result = self.strategy.analyze("")
        assert result["sentiment"] == "neutral"
        assert result["polarity"] == 0.0
        assert result["subjectivity"] == 0.0
    
    def test_whitespace_only(self):
        """Test handling of whitespace-only text"""
        result = self.strategy.analyze("   \n\t   ")
        assert result["sentiment"] == "neutral"
        assert result["polarity"] == 0.0
        assert result["subjectivity"] == 0.0
    
    def test_result_structure(self):
        """Test that result has expected structure"""
        text = "This is a test sentence."
        result = self.strategy.analyze(text)
        
        expected_keys = {"sentiment", "polarity", "subjectivity"}
        assert set(result.keys()) == expected_keys 