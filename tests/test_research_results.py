"""
Tests for Research Results Management
"""

import os
import json
import tempfile
import shutil
import unittest

from src.research.research_results import ResearchResult, ResearchResultManager


class TestResearchResult(unittest.TestCase):
    """Test ResearchResult dataclass."""

    def test_result_creation(self):
        """Test creating a research result."""
        result = ResearchResult(
            result_id="test-123",
            title="Test Result",
            category="keywords",
            data={"keywords": ["nike", "shoes"]},
            source="google_trends",
            tags=["fashion", "egypt"]
        )
        
        self.assertEqual(result.result_id, "test-123")
        self.assertEqual(result.title, "Test Result")
        self.assertIsNotNone(result.created_at)

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = ResearchResult(
            result_id="test-123",
            title="Test Result",
            category="keywords",
            data={"keywords": ["nike"]},
            source="google_trends",
            tags=["fashion"]
        )
        
        result_dict = result.to_dict()
        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict["result_id"], "test-123")
        self.assertEqual(result_dict["title"], "Test Result")

    def test_result_from_dict(self):
        """Test creating result from dictionary."""
        result_dict = {
            "result_id": "test-123",
            "task_id": None,
            "title": "Test Result",
            "category": "keywords",
            "data": {"keywords": ["nike"]},
            "source": "google_trends",
            "tags": ["fashion"],
            "brand": None,
            "channel": None,
            "product_id": None,
            "created_at": "2024-01-01T00:00:00Z",
            "notes": None,
            "confidence_score": None
        }
        
        result = ResearchResult.from_dict(result_dict)
        self.assertEqual(result.result_id, "test-123")
        self.assertEqual(result.title, "Test Result")


class TestResearchResultManager(unittest.TestCase):
    """Test ResearchResultManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ResearchResultManager(data_dir=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_save_result(self):
        """Test saving a new result."""
        result = self.manager.save_result(
            title="Test Result",
            category="keywords",
            data={"keywords": ["nike", "shoes"]},
            source="google_trends",
            tags=["fashion"]
        )
        
        self.assertIsNotNone(result.result_id)
        self.assertEqual(result.title, "Test Result")
        self.assertEqual(result.category, "keywords")

    def test_get_result(self):
        """Test retrieving a result by ID."""
        result = self.manager.save_result(
            title="Test Result",
            category="keywords",
            data={"keywords": ["nike"]},
            source="google_trends",
            tags=["fashion"]
        )
        
        retrieved = self.manager.get_result(result.result_id)
        self.assertEqual(retrieved.result_id, result.result_id)
        self.assertEqual(retrieved.title, "Test Result")

    def test_get_nonexistent_result(self):
        """Test retrieving a non-existent result."""
        retrieved = self.manager.get_result("nonexistent-id")
        self.assertIsNone(retrieved)

    def test_search_by_tag(self):
        """Test searching results by tag."""
        self.manager.save_result(
            title="Result 1",
            category="keywords",
            data={"keywords": ["nike"]},
            source="google_trends",
            tags=["fashion", "egypt"]
        )
        
        self.manager.save_result(
            title="Result 2",
            category="competitors",
            data={"competitors": ["adidas"]},
            source="similarweb",
            tags=["electronics"]
        )
        
        fashion_results = self.manager.search_by_tag("fashion")
        self.assertEqual(len(fashion_results), 1)
        self.assertEqual(fashion_results[0].title, "Result 1")

    def test_search_by_brand(self):
        """Test searching results by brand."""
        self.manager.save_result(
            title="Nike Result",
            category="keywords",
            data={"keywords": ["nike"]},
            source="google_trends",
            tags=["fashion"],
            brand="Nike"
        )
        
        self.manager.save_result(
            title="Adidas Result",
            category="keywords",
            data={"keywords": ["adidas"]},
            source="google_trends",
            tags=["fashion"],
            brand="Adidas"
        )
        
        nike_results = self.manager.search_by_brand("Nike")
        self.assertEqual(len(nike_results), 1)
        self.assertEqual(nike_results[0].brand, "Nike")

    def test_search_by_channel(self):
        """Test searching results by channel."""
        self.manager.save_result(
            title="Facebook Result",
            category="social_media",
            data={"insights": {}},
            source="facebook_insights",
            tags=["social"],
            channel="facebook"
        )
        
        self.manager.save_result(
            title="Instagram Result",
            category="social_media",
            data={"insights": {}},
            source="facebook_insights",
            tags=["social"],
            channel="instagram"
        )
        
        fb_results = self.manager.search_by_channel("facebook")
        self.assertEqual(len(fb_results), 1)
        self.assertEqual(fb_results[0].channel, "facebook")

    def test_search_by_category(self):
        """Test searching results by category."""
        self.manager.save_result(
            title="Keyword Result",
            category="keywords",
            data={"keywords": ["nike"]},
            source="google_trends",
            tags=["fashion"]
        )
        
        self.manager.save_result(
            title="Competitor Result",
            category="competitors",
            data={"competitors": ["adidas"]},
            source="similarweb",
            tags=["fashion"]
        )
        
        keyword_results = self.manager.search_by_category("keywords")
        self.assertEqual(len(keyword_results), 1)
        self.assertEqual(keyword_results[0].category, "keywords")

    def test_search_by_product(self):
        """Test searching results by product ID."""
        self.manager.save_result(
            title="Product Result",
            category="keywords",
            data={"keywords": ["nike"]},
            source="google_trends",
            tags=["fashion"],
            product_id="prod-123"
        )
        
        self.manager.save_result(
            title="Other Result",
            category="keywords",
            data={"keywords": ["adidas"]},
            source="google_trends",
            tags=["fashion"],
            product_id="prod-456"
        )
        
        product_results = self.manager.search_by_product("prod-123")
        self.assertEqual(len(product_results), 1)
        self.assertEqual(product_results[0].product_id, "prod-123")

    def test_list_results(self):
        """Test listing all results."""
        self.manager.save_result(
            title="Result 1",
            category="keywords",
            data={"keywords": ["nike"]},
            source="google_trends",
            tags=["fashion"]
        )
        
        self.manager.save_result(
            title="Result 2",
            category="competitors",
            data={"competitors": ["adidas"]},
            source="similarweb",
            tags=["fashion"]
        )
        
        results = self.manager.list_results()
        self.assertEqual(len(results), 2)

    def test_list_results_with_filter(self):
        """Test listing results with category filter."""
        self.manager.save_result(
            title="Result 1",
            category="keywords",
            data={"keywords": ["nike"]},
            source="google_trends",
            tags=["fashion"]
        )
        
        self.manager.save_result(
            title="Result 2",
            category="competitors",
            data={"competitors": ["adidas"]},
            source="similarweb",
            tags=["fashion"]
        )
        
        keyword_results = self.manager.list_results(category="keywords")
        self.assertEqual(len(keyword_results), 1)
        self.assertEqual(keyword_results[0].category, "keywords")

    def test_list_results_with_limit(self):
        """Test listing results with limit."""
        for i in range(5):
            self.manager.save_result(
                title=f"Result {i}",
                category="keywords",
                data={"keywords": [f"keyword{i}"]},
                source="google_trends",
                tags=["test"]
            )
        
        results = self.manager.list_results(limit=3)
        self.assertEqual(len(results), 3)

    def test_update_result(self):
        """Test updating a result."""
        result = self.manager.save_result(
            title="Original Title",
            category="keywords",
            data={"keywords": ["nike"]},
            source="google_trends",
            tags=["fashion"]
        )
        
        updated = self.manager.update_result(
            result.result_id,
            title="Updated Title",
            data={"keywords": ["nike", "shoes"]},
            confidence_score=0.9
        )
        
        self.assertEqual(updated.title, "Updated Title")
        self.assertEqual(updated.data["keywords"], ["nike", "shoes"])
        self.assertEqual(updated.confidence_score, 0.9)

    def test_delete_result(self):
        """Test deleting a result."""
        result = self.manager.save_result(
            title="Test Result",
            category="keywords",
            data={"keywords": ["nike"]},
            source="google_trends",
            tags=["fashion"]
        )
        
        success = self.manager.delete_result(result.result_id)
        self.assertTrue(success)
        
        retrieved = self.manager.get_result(result.result_id)
        self.assertIsNone(retrieved)

    def test_delete_nonexistent_result(self):
        """Test deleting a non-existent result."""
        success = self.manager.delete_result("nonexistent-id")
        self.assertFalse(success)

    def test_get_statistics(self):
        """Test getting result statistics."""
        self.manager.save_result(
            title="Result 1",
            category="keywords",
            data={"keywords": ["nike"]},
            source="google_trends",
            tags=["fashion"]
        )
        
        self.manager.save_result(
            title="Result 2",
            category="competitors",
            data={"competitors": ["adidas"]},
            source="similarweb",
            tags=["fashion"]
        )
        
        stats = self.manager.get_statistics()
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["by_category"]["keywords"], 1)
        self.assertEqual(stats["by_category"]["competitors"], 1)
        self.assertEqual(stats["by_source"]["google_trends"], 1)
        self.assertEqual(stats["by_source"]["similarweb"], 1)

    def test_persistence(self):
        """Test that results persist across manager instances."""
        result = self.manager.save_result(
            title="Test Result",
            category="keywords",
            data={"keywords": ["nike"]},
            source="google_trends",
            tags=["fashion"]
        )
        
        # Create new manager with same directory
        new_manager = ResearchResultManager(data_dir=self.temp_dir)
        retrieved = new_manager.get_result(result.result_id)
        
        self.assertEqual(retrieved.result_id, result.result_id)
        self.assertEqual(retrieved.title, result.title)

    def test_result_with_task_association(self):
        """Test creating result with task association."""
        result = self.manager.save_result(
            title="Task Result",
            category="keywords",
            data={"keywords": ["nike"]},
            source="google_trends",
            tags=["fashion"],
            task_id="task-123"
        )
        
        self.assertEqual(result.task_id, "task-123")

    def test_result_with_confidence_score(self):
        """Test creating result with confidence score."""
        result = self.manager.save_result(
            title="High Confidence Result",
            category="keywords",
            data={"keywords": ["nike"]},
            source="google_trends",
            tags=["fashion"],
            confidence_score=0.95
        )
        
        self.assertEqual(result.confidence_score, 0.95)

    def test_result_with_notes(self):
        """Test creating result with notes."""
        result = self.manager.save_result(
            title="Noted Result",
            category="keywords",
            data={"keywords": ["nike"]},
            source="google_trends",
            tags=["fashion"],
            notes="Research conducted on 2024-01-15"
        )
        
        self.assertEqual(result.notes, "Research conducted on 2024-01-15")

    def test_filter_by_multiple_tags(self):
        """Test filtering results by multiple tags."""
        self.manager.save_result(
            title="Result 1",
            category="keywords",
            data={"keywords": ["nike"]},
            source="google_trends",
            tags=["fashion", "egypt", "shoes"]
        )
        
        self.manager.save_result(
            title="Result 2",
            category="keywords",
            data={"keywords": ["adidas"]},
            source="google_trends",
            tags=["fashion", "shoes"]
        )
        
        self.manager.save_result(
            title="Result 3",
            category="keywords",
            data={"keywords": ["puma"]},
            source="google_trends",
            tags=["fashion"]
        )
        
        # Filter for results with both "fashion" and "egypt"
        results = self.manager.list_results(tags=["fashion", "egypt"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Result 1")

    def test_sorting_by_created_at(self):
        """Test that results are sorted by created_at (newest first)."""
        result1 = self.manager.save_result(
            title="First Result",
            category="keywords",
            data={"keywords": ["nike"]},
            source="google_trends",
            tags=["fashion"]
        )
        
        result2 = self.manager.save_result(
            title="Second Result",
            category="keywords",
            data={"keywords": ["adidas"]},
            source="google_trends",
            tags=["fashion"]
        )
        
        results = self.manager.list_results()
        self.assertEqual(results[0].result_id, result2.result_id)
        self.assertEqual(results[1].result_id, result1.result_id)


if __name__ == "__main__":
    unittest.main()
