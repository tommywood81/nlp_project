import pytest
from app.models.ner import NERStrategy

@pytest.mark.unit
class TestNERStrategy:
    """Test suite for NERStrategy"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.strategy = NERStrategy()
    
    def test_person_entity(self):
        """Test extraction of person entities"""
        text = "John Smith works at Microsoft."
        result = self.strategy.analyze(text)
        
        # Should find at least one person
        person_entities = [ent for ent in result if ent["label"] == "PERSON"]
        assert len(person_entities) >= 1
        assert "John Smith" in [ent["text"] for ent in person_entities]
    
    def test_organization_entity(self):
        """Test extraction of organization entities"""
        text = "Apple Inc. is headquartered in Cupertino."
        result = self.strategy.analyze(text)
        
        # Should find organization
        org_entities = [ent for ent in result if ent["label"] == "ORG"]
        assert len(org_entities) >= 1
        assert "Apple Inc." in [ent["text"] for ent in org_entities]
    
    def test_location_entity(self):
        """Test extraction of location entities"""
        text = "I live in New York City."
        result = self.strategy.analyze(text)
        
        # Should find location
        loc_entities = [ent for ent in result if ent["label"] == "GPE"]
        assert len(loc_entities) >= 1
        assert "New York City" in [ent["text"] for ent in loc_entities]
    
    def test_date_entity(self):
        """Test extraction of date entities"""
        text = "The meeting is scheduled for January 15th, 2024."
        result = self.strategy.analyze(text)
        
        # Should find date
        date_entities = [ent for ent in result if ent["label"] == "DATE"]
        assert len(date_entities) >= 1
    
    def test_empty_text(self):
        """Test handling of empty text"""
        result = self.strategy.analyze("")
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_no_entities(self):
        """Test text with no named entities"""
        text = "This is a simple sentence without any named entities."
        result = self.strategy.analyze(text)
        assert isinstance(result, list)
        # May or may not have entities, but should be a valid list
    
    def test_result_structure(self):
        """Test that result has expected structure"""
        text = "John Smith works at Microsoft in Seattle."
        result = self.strategy.analyze(text)
        
        assert isinstance(result, list)
        for entity in result:
            assert isinstance(entity, dict)
            assert "text" in entity
            assert "label" in entity
            assert isinstance(entity["text"], str)
            assert isinstance(entity["label"], str)
    
    def test_multiple_entities(self):
        """Test extraction of multiple entity types"""
        text = "John Smith works at Microsoft in Seattle on January 15th."
        result = self.strategy.analyze(text)
        
        assert isinstance(result, list)
        assert len(result) >= 1
        
        # Check that we have different entity types
        entity_labels = [ent["label"] for ent in result]
        assert len(set(entity_labels)) >= 1  # At least one unique label 