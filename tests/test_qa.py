import pytest
from app.models.qa import QAStrategy

@pytest.mark.unit
@pytest.mark.slow
class TestQAStrategy:
    """Test suite for QAStrategy"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.strategy = QAStrategy()
    
    def test_basic_question_answering(self):
        """Test basic question answering functionality"""
        question = "What is the capital of France?"
        context = "Paris is the capital and largest city of France. It is known for its art, fashion, and culture."
        
        result = self.strategy.analyze(question, context)
        
        assert "answer" in result
        assert "score" in result
        assert isinstance(result["answer"], str)
        assert isinstance(result["score"], float)
        assert len(result["answer"]) > 0
        assert 0.0 <= result["score"] <= 1.0
    
    def test_who_question(self):
        """Test 'who' type questions"""
        question = "Who created Python?"
        context = "Python was created by Guido van Rossum and first released in 1991."
        
        result = self.strategy.analyze(question, context)
        
        assert "answer" in result
        assert "score" in result
        assert isinstance(result["answer"], str)
        assert isinstance(result["score"], float)
        assert len(result["answer"]) > 0
    
    def test_when_question(self):
        """Test 'when' type questions"""
        question = "When was Python first released?"
        context = "Python was created by Guido van Rossum and first released in 1991."
        
        result = self.strategy.analyze(question, context)
        
        assert "answer" in result
        assert "score" in result
        assert isinstance(result["answer"], str)
        assert isinstance(result["score"], float)
        assert len(result["answer"]) > 0
    
    def test_where_question(self):
        """Test 'where' type questions"""
        question = "Where is the Eiffel Tower located?"
        context = "The Eiffel Tower is located in Paris, France. It was built in 1889."
        
        result = self.strategy.analyze(question, context)
        
        assert "answer" in result
        assert "score" in result
        assert isinstance(result["answer"], str)
        assert isinstance(result["score"], float)
        assert len(result["answer"]) > 0
    
    def test_empty_question(self):
        """Test handling of empty question"""
        question = ""
        context = "This is some context."
        
        with pytest.raises(Exception):
            self.strategy.analyze(question, context)
    
    def test_empty_context(self):
        """Test handling of empty context"""
        question = "What is this about?"
        context = ""
        
        with pytest.raises(Exception):
            self.strategy.analyze(question, context)
    
    def test_whitespace_only_question(self):
        """Test handling of whitespace-only question"""
        question = "   \n\t   "
        context = "This is some context."
        
        with pytest.raises(Exception):
            self.strategy.analyze(question, context)
    
    def test_whitespace_only_context(self):
        """Test handling of whitespace-only context"""
        question = "What is this about?"
        context = "   \n\t   "
        
        with pytest.raises(Exception):
            self.strategy.analyze(question, context)
    
    def test_result_structure(self):
        """Test that result has expected structure"""
        question = "What is AI?"
        context = "Artificial Intelligence (AI) is a branch of computer science."
        
        result = self.strategy.analyze(question, context)
        
        assert isinstance(result, dict)
        assert "answer" in result
        assert "score" in result
        assert isinstance(result["answer"], str)
        assert isinstance(result["score"], float)
    
    def test_score_range(self):
        """Test that confidence score is within valid range"""
        question = "What is machine learning?"
        context = "Machine learning is a subset of artificial intelligence."
        
        result = self.strategy.analyze(question, context)
        
        assert 0.0 <= result["score"] <= 1.0
    
    def test_complex_context(self):
        """Test question answering with complex context"""
        question = "What are the main applications of NLP?"
        context = """
        Natural Language Processing (NLP) has many applications including 
        machine translation, sentiment analysis, text summarization, 
        question answering, and chatbots. It is used in various industries 
        such as healthcare, finance, and customer service.
        """
        
        result = self.strategy.analyze(question, context)
        
        assert "answer" in result
        assert "score" in result
        assert isinstance(result["answer"], str)
        assert isinstance(result["score"], float)
        assert len(result["answer"]) > 0
    
    def test_answer_in_context(self):
        """Test that the answer is found within the provided context"""
        question = "What is the weather like?"
        context = "The weather today is sunny and warm with a temperature of 25 degrees Celsius."
        
        result = self.strategy.analyze(question, context)
        
        # The answer should be a substring of the context
        answer_lower = result["answer"].lower()
        context_lower = context.lower()
        
        # Check if answer words appear in context (allowing for variations)
        answer_words = answer_lower.split()
        context_words = context_lower.split()
        
        # At least some words from the answer should be in the context
        common_words = set(answer_words) & set(context_words)
        assert len(common_words) > 0 