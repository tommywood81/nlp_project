import pytest
from app.models.emotion import EmotionStrategy

@pytest.mark.unit
@pytest.mark.slow
class TestEmotionStrategy:
    """Test suite for EmotionStrategy"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.strategy = EmotionStrategy()
    
    def test_joy_emotion(self):
        """Test detection of joy emotion"""
        text = "I'm so happy and excited about this wonderful news!"
        result = self.strategy.analyze(text)
        
        assert "label" in result
        assert "score" in result
        assert isinstance(result["label"], str)
        assert isinstance(result["score"], float)
        assert 0.0 <= result["score"] <= 1.0
    
    def test_sadness_emotion(self):
        """Test detection of sadness emotion"""
        text = "I feel so sad and depressed about what happened."
        result = self.strategy.analyze(text)
        
        assert "label" in result
        assert "score" in result
        assert isinstance(result["label"], str)
        assert isinstance(result["score"], float)
        assert 0.0 <= result["score"] <= 1.0
    
    def test_anger_emotion(self):
        """Test detection of anger emotion"""
        text = "I'm furious and angry about this terrible situation!"
        result = self.strategy.analyze(text)
        
        assert "label" in result
        assert "score" in result
        assert isinstance(result["label"], str)
        assert isinstance(result["score"], float)
        assert 0.0 <= result["score"] <= 1.0
    
    def test_neutral_emotion(self):
        """Test detection of neutral emotion"""
        text = "This is a factual statement about the weather."
        result = self.strategy.analyze(text)
        
        assert "label" in result
        assert "score" in result
        assert isinstance(result["label"], str)
        assert isinstance(result["score"], float)
        assert 0.0 <= result["score"] <= 1.0
    
    def test_empty_text(self):
        """Test handling of empty text"""
        with pytest.raises(Exception):
            self.strategy.analyze("")
    
    def test_whitespace_only(self):
        """Test handling of whitespace-only text"""
        with pytest.raises(Exception):
            self.strategy.analyze("   \n\t   ")
    
    def test_result_structure(self):
        """Test that result has expected structure"""
        text = "I'm feeling quite happy today."
        result = self.strategy.analyze(text)
        
        assert isinstance(result, dict)
        assert "label" in result
        assert "score" in result
        assert isinstance(result["label"], str)
        assert isinstance(result["score"], float)
    
    def test_score_range(self):
        """Test that confidence score is within valid range"""
        text = "I'm feeling mixed emotions about this."
        result = self.strategy.analyze(text)
        
        assert 0.0 <= result["score"] <= 1.0
    
    def test_emotion_labels(self):
        """Test that emotion labels are valid"""
        valid_emotions = {"joy", "sadness", "anger", "fear", "surprise", "love", "neutral"}
        
        test_texts = [
            "I'm so happy!",
            "I'm very sad.",
            "I'm angry!",
            "I'm scared.",
            "I'm surprised!",
            "I love this!",
            "This is neutral."
        ]
        
        for text in test_texts:
            result = self.strategy.analyze(text)
            assert result["label"] in valid_emotions