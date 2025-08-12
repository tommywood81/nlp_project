import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.mark.integration
class TestIntegration:
    """Integration tests for the FastAPI application"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_home_page(self):
        """Test the home page endpoint"""
        response = self.client.get("/home")
        assert response.status_code == 200
        assert "NLP Portfolio Dashboard" in response.text
        assert "Analyse Your Own Text" in response.text
        assert "Analyse Live ABC News" in response.text
    
    def test_main_analysis_page(self):
        """Test the main analysis page"""
        response = self.client.get("/")
        assert response.status_code == 200
        assert "Analyse Your Own Text" in response.text
        assert "Sentiment" in response.text
        assert "NER" in response.text
        assert "Summarise" in response.text
        assert "Emotion" in response.text
        assert "QA" in response.text
    
    def test_news_browse_page(self):
        """Test the news browse page"""
        response = self.client.get("/news/browse")
        assert response.status_code == 200
        assert "ABC News" in response.text
        assert "Top Stories" in response.text
        assert "Australia" in response.text
        assert "Just In" in response.text
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis endpoint"""
        data = {"text": "I love this amazing product!"}
        response = self.client.post("/analyze/sentiment", data=data)
        assert response.status_code == 200
        assert "positive" in response.text.lower()
    
    def test_ner_analysis(self):
        """Test NER analysis endpoint"""
        data = {"text": "John Smith works at Microsoft in Seattle."}
        response = self.client.post("/analyze/ner", data=data)
        assert response.status_code == 200
        assert "PERSON" in response.text or "ORG" in response.text or "GPE" in response.text
    
    def test_summarize_analysis(self):
        """Test summarization endpoint"""
        text = """
        Artificial intelligence (AI) is intelligence demonstrated by machines, 
        in contrast to the natural intelligence displayed by humans and animals. 
        Leading AI textbooks define the field as the study of "intelligent agents": 
        any device that perceives its environment and takes actions that maximize 
        its chance of successfully achieving its goals.
        """
        data = {"text": text}
        response = self.client.post("/analyze/summarize", data=data)
        assert response.status_code == 200
        assert "summary" in response.text.lower()
    
    def test_emotion_analysis(self):
        """Test emotion analysis endpoint"""
        data = {"text": "I'm so happy and excited about this wonderful news!"}
        response = self.client.post("/analyze/emotion", data=data)
        assert response.status_code == 200
        assert "joy" in response.text.lower() or "label" in response.text.lower()
    
    def test_qa_analysis(self):
        """Test question answering endpoint"""
        data = {
            "text": "What is the capital of France?",
            "context": "Paris is the capital and largest city of France."
        }
        response = self.client.post("/analyze/qa", data=data)
        assert response.status_code == 200
        assert "answer" in response.text.lower()
    
    def test_empty_text_handling(self):
        """Test handling of empty text input"""
        data = {"text": ""}
        response = self.client.post("/analyze/sentiment", data=data)
        assert response.status_code == 200  # Should handle gracefully
    
    def test_missing_text_parameter(self):
        """Test handling of missing text parameter"""
        data = {}  # No text parameter
        response = self.client.post("/analyze/sentiment", data=data)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_task_parameter(self):
        """Test handling of invalid task parameter"""
        data = {"text": "Test text"}
        response = self.client.post("/analyze/invalid_task", data=data)
        assert response.status_code == 200  # Should show error page
    
    def test_static_files(self):
        """Test that static files are served correctly"""
        response = self.client.get("/static/style.css")
        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")
    
    def test_news_feed_api(self):
        """Test the news feed API endpoint"""
        response = self.client.get("/news")
        # This might fail due to network issues, but should not crash
        assert response.status_code in [200, 500]  # Either success or network error
    
    def test_news_analysis_endpoint(self):
        """Test the news analysis endpoint"""
        response = self.client.get("/news/analyze?feed_name=top_stories&index=0&tools=sentiment")
        # This might fail due to network issues, but should not crash
        assert response.status_code in [200, 500]  # Either success or network error
    
    def test_qa_missing_context(self):
        """Test QA with missing context"""
        data = {"text": "What is this?"}  # Missing context
        response = self.client.post("/analyze/qa", data=data)
        assert response.status_code == 200  # Should handle gracefully
    
    def test_long_text_handling(self):
        """Test handling of very long text"""
        long_text = "This is a test. " * 1000  # Very long text
        data = {"text": long_text}
        response = self.client.post("/analyze/sentiment", data=data)
        assert response.status_code == 200  # Should handle gracefully
    
    def test_special_characters(self):
        """Test handling of special characters"""
        text_with_special_chars = "Test with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        data = {"text": text_with_special_chars}
        response = self.client.post("/analyze/sentiment", data=data)
        assert response.status_code == 200
    
    def test_unicode_characters(self):
        """Test handling of unicode characters"""
        unicode_text = "Test with unicode: café, naïve, résumé, 你好, مرحبا"
        data = {"text": unicode_text}
        response = self.client.post("/analyze/sentiment", data=data)
        assert response.status_code == 200
    
    def test_multiple_tools_analysis(self):
        """Test analysis with multiple tools"""
        data = {"text": "John Smith loves this amazing product from Microsoft!"}
        
        # Test each tool individually
        tools = ["sentiment", "ner", "summarize", "emotion"]
        for tool in tools:
            response = self.client.post(f"/analyze/{tool}", data=data)
            assert response.status_code == 200
    
    def test_response_headers(self):
        """Test that response headers are set correctly"""
        response = self.client.get("/home")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_error_handling(self):
        """Test error handling for malformed requests"""
        # Test with invalid JSON
        response = self.client.post("/analyze/sentiment", data="invalid json", headers={"content-type": "application/json"})
        assert response.status_code in [422, 400]  # Should handle gracefully
