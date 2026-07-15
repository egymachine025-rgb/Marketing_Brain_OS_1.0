import json
import os
import shutil
import tempfile
import unittest

from marketing_brain_os.dashboard_repository import DashboardRepository
from marketing_brain_os.dashboard_service import DashboardService
import importlib


class TestIntelligenceApi(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_api_intel_")
        self.repo = DashboardRepository(data_dir=self.temp_dir)
        self.service = DashboardService(repo=self.repo)
        self.api_app = importlib.import_module("src.api.app")
        self.api_app.dashboard_service = self.service
        self.client = self.api_app.app.test_client()

        self.product = {
            "product_id": "tg-intel-001",
            "listing": {
                "title": "Samsung Galaxy S23",
                "description": "Latest Galaxy phone with premium features.",
                "price": {"amount": 1200.0, "currency": "USD"},
                "category": "tech",
            },
            "seller": {"username": "seller_egy", "display_name": "Seller EG"},
            "metadata": {"acquired_at": "2024-07-01T10:00:00Z"},
            "status": "active",
        }
        product_path = os.path.join(self.temp_dir, f"{self.product['product_id']}.json")
        with open(product_path, "w", encoding="utf-8") as f:
            json.dump(self.product, f)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_get_newest_products_intelligence(self):
        response = self.client.get("/api/intelligence/products/newest?limit=1")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("data", data)
        products = data["data"]["products"]
        self.assertEqual(len(products), 1)
        intel = products[0]
        self.assertEqual(intel["product_id"], self.product["product_id"])
        self.assertIn("content_analysis", intel)
        self.assertIn("sales_hooks", intel)

    def test_get_product_intelligence(self):
        response = self.client.get(f"/api/intelligence/product/{self.product['product_id']}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        intel = data["data"]
        self.assertEqual(intel["product_id"], self.product["product_id"])
        self.assertEqual(intel["title"], self.product["listing"]["title"])
        self.assertGreaterEqual(len(intel["sales_hooks"]), 1)
        self.assertIn("keyword_data", intel)

    def test_get_product_intelligence_not_found(self):
        response = self.client.get("/api/intelligence/product/missing-id")
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertIn("error", data)

    def test_get_market_segments(self):
        response = self.client.get("/api/intelligence/market-segments")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("market_data", data["data"])
        self.assertIn("segments", data["data"])
        self.assertIn("platform_insights", data["data"])
        self.assertIn("regional_insights", data["data"])
        
        market_data = data["data"]["market_data"]
        self.assertIn("total_population", market_data)
        self.assertIn("internet_users", market_data)
        self.assertIn("social_media_users", market_data)
        
        segments = data["data"]["segments"]
        self.assertGreater(len(segments), 0)
        segment = segments[0]
        self.assertIn("segment_name", segment)
        self.assertIn("income_range", segment)
        self.assertIn("income_min", segment)
        self.assertIn("income_max", segment)
        self.assertIn("areas", segment)
        self.assertIn("social_media_platforms", segment)
        self.assertIn("population_percentage", segment)
        
        platform_insights = data["data"]["platform_insights"]
        self.assertIn("facebook", platform_insights)
        self.assertIn("instagram", platform_insights)
        
        regional_insights = data["data"]["regional_insights"]
        self.assertIn("cairo", regional_insights)
        self.assertIn("alexandria", regional_insights)

    def test_get_content_strategy(self):
        response = self.client.get(f"/api/intelligence/content-strategy?product_id={self.product['product_id']}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        
        strategy = data["data"]
        self.assertEqual(strategy["product_id"], self.product["product_id"])
        self.assertIn("content_analysis", strategy)
        self.assertIn("market_insights", strategy)
        self.assertIn("platform_recommendations", strategy)
        self.assertIn("best_posting_times", strategy)
        self.assertIn("content_suggestions", strategy)
        self.assertIn("content_type", strategy)
        self.assertIn("caption_style", strategy)
        self.assertIn("hashtags", strategy)
        self.assertIn("target_segment", strategy)
        
        platform_rec = strategy["platform_recommendations"]
        self.assertIn("primary", platform_rec)
        self.assertIn("secondary", platform_rec)
        self.assertIn("reasoning", platform_rec)
        self.assertIn("segment_alignment", platform_rec)
        
        content_type = strategy["content_type"]
        self.assertIn("primary", content_type)
        self.assertIn("secondary", content_type)
        self.assertIn("reasoning", content_type)
        
        caption_style = strategy["caption_style"]
        self.assertIn("tone", caption_style)
        self.assertIn("language", caption_style)
        self.assertIn("example", caption_style)
        
        hashtags = strategy["hashtags"]
        self.assertIn("primary", hashtags)
        self.assertIn("category", hashtags)
        self.assertIn("segment", hashtags)
        self.assertIn("all", hashtags)
        
        content_suggestions = strategy["content_suggestions"]
        self.assertIn("headlines", content_suggestions)
        self.assertIn("call_to_action", content_suggestions)
        self.assertIn("hashtag_suggestions", content_suggestions)

    def test_get_content_strategy_missing_product_id(self):
        response = self.client.get("/api/intelligence/content-strategy")
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertIn("error", data)

    def test_get_content_strategy_product_not_found(self):
        response = self.client.get("/api/intelligence/content-strategy?product_id=non-existent")
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertIn("error", data)

    def test_get_keywords(self):
        response = self.client.get("/api/intelligence/keywords?category=tech")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        
        keywords_data = data["data"]
        self.assertEqual(keywords_data["category"], "tech")
        self.assertIn("low_competition_keywords", keywords_data)
        self.assertIn("competitor_analysis", keywords_data)
        self.assertIn("keyword_suggestions", keywords_data)
        
        keyword_suggestions = keywords_data["keyword_suggestions"]
        self.assertGreater(len(keyword_suggestions), 0)
        keyword = keyword_suggestions[0]
        self.assertIn("keyword", keyword)
        self.assertIn("competition", keyword)
        self.assertIn("search_volume", keyword)
        self.assertIn("cpc_egp", keyword)
        self.assertIn("difficulty", keyword)
        
        # Verify data types
        self.assertIsInstance(keyword["search_volume"], int)
        self.assertIsInstance(keyword["cpc_egp"], (int, float))
        self.assertIsInstance(keyword["difficulty"], int)

    def test_get_keywords_no_category(self):
        response = self.client.get("/api/intelligence/keywords")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["category"], "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
