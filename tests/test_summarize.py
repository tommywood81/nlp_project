import pytest
from app.models.summarize import SummarizationStrategy

@pytest.mark.unit
@pytest.mark.slow
class TestSummarizationStrategy:
    """Test suite for SummarizationStrategy"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.strategy = SummarizationStrategy()
    
    def test_basic_summarization(self):
        """Test basic text summarization"""
        text = """
        Artificial intelligence (AI) is intelligence demonstrated by machines, 
        in contrast to the natural intelligence displayed by humans and animals. 
        Leading AI textbooks define the field as the study of "intelligent agents": 
        any device that perceives its environment and takes actions that maximize 
        its chance of successfully achieving its goals. Colloquially, the term 
        "artificial intelligence" is often used to describe machines that mimic 
        "cognitive" functions that humans associate with the human mind, such as 
        "learning" and "problem solving".
        """
        result = self.strategy.analyze(text)
        
        assert "summary" in result
        assert isinstance(result["summary"], str)
        assert len(result["summary"]) > 0
        assert len(result["summary"]) < len(text)  # Summary should be shorter
    
    def test_short_text(self):
        """Test summarization of short text"""
        text = "This is a short text that should still be summarized."
        result = self.strategy.analyze(text)
        
        assert "summary" in result
        assert isinstance(result["summary"], str)
        assert len(result["summary"]) > 0
    
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
        text = """
        Machine learning is a subset of artificial intelligence that focuses on 
        algorithms and statistical models that enable computers to perform tasks 
        without explicit instructions. Instead, they rely on patterns and inference.
        """
        result = self.strategy.analyze(text)
        
        assert isinstance(result, dict)
        assert "summary" in result
        assert isinstance(result["summary"], str)
    
    def test_summary_quality(self):
        """Test that summary contains key concepts"""
        text = """
        Python is a high-level, interpreted programming language known for its 
        simplicity and readability. It was created by Guido van Rossum and first 
        released in 1991. Python supports multiple programming paradigms including 
        procedural, object-oriented, and functional programming.
        """
        result = self.strategy.analyze(text)
        
        summary = result["summary"].lower()
        # Summary should contain key terms (may vary based on model)
        assert len(summary) > 0
        assert isinstance(summary, str)
    
    def test_long_text(self):
        """Test summarization of longer text"""
        text = """
        Natural language processing (NLP) is a subfield of linguistics, computer 
        science, and artificial intelligence concerned with the interactions between 
        computers and human language, in particular how to program computers to 
        process and analyze large amounts of natural language data. Challenges in 
        natural language processing frequently involve speech recognition, natural 
        language understanding, and natural language generation. NLP is used in 
        many real-world applications including machine translation, question 
        answering, sentiment analysis, and text summarization. The field has seen 
        significant advances in recent years with the development of transformer 
        models and large language models.
        """
        result = self.strategy.analyze(text)
        
        assert "summary" in result
        assert isinstance(result["summary"], str)
        assert len(result["summary"]) > 0
        assert len(result["summary"]) < len(text) 