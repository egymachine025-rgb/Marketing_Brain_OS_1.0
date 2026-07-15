import unittest
import uuid
from datetime import datetime
from marketing_brain_os.product import Product
from marketing_brain_os.normalizer import ProductNormalizer
from src.models.base import Currency

class TestProductNormalizer(unittest.TestCase):
    def setUp(self) -> None:
        self.normalizer = ProductNormalizer()
        self.product = Product(
            id=uuid.uuid4(),
            fingerprint="temp_fingerprint",
            name="Raw Iphone 16gb",
            brand="iphone",
            category="tech",
            description="Brand new model with 16gb of ram and weighs only 10lbs.",
            price=999.987,
            currency=Currency.USD,
            colors=["BLACK", "Rose Gold", "ugly-neon-color"],
            features=["- wireless charging ", "*waterproof resistant"],
            images=[],
            videos=[]
        )

    def test_normalization_pipeline(self) -> None:
        normalized_product = self.normalizer.normalize_product(self.product)

        # Brand map checks
        self.assertEqual(normalized_product.brand, "Apple")
        
        # Category map checks
        self.assertEqual(normalized_product.category, "Electronics")
        
        # Pricing precision checks
        self.assertEqual(normalized_product.price, 999.99) # round(999.987, 2) == 999.99, standard rounding
        
        # Color mapping checks (Filters bad colors and standardizes formatting)
        self.assertIn("black", normalized_product.colors)
        self.assertIn("rose gold", normalized_product.colors)
        self.assertNotIn("ugly-neon-color", normalized_product.colors)

        # Feature syntax checks
        self.assertIn("Wireless charging", normalized_product.features)
        self.assertIn("Waterproof resistant", normalized_product.features)

        # Text unit check
        self.assertIn("16 GB", normalized_product.name)
        self.assertIn("16 GB", normalized_product.description)
        self.assertIn("10 lbs", normalized_product.description)

        # Recalculated fingerprint check
        self.assertNotEqual(normalized_product.fingerprint, "temp_fingerprint")

if __name__ == "__main__":
    unittest.main()