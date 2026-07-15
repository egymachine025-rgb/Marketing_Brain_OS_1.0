from __future__ import annotations
import json
import os
from typing import Any, Dict, Optional
from marketing_brain_os.product import Product

class ProductRepository:
    """
    مستودع حقيقي لحفظ المنتجات في ملفات JSON لحين ترحيلها إلى قاعدة البيانات الكبيرة.
    """
    def __init__(self, filepath: str = "data/products.json") -> None:
        self.filepath = filepath
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def save(self, product: Product) -> Product:
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        data[str(product.id)] = product.to_dict()
        
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return product

    def get_by_fingerprint(self, fingerprint: str) -> Optional[Dict[str, Any]]:
        if not os.path.exists(self.filepath):
            return None
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        for prod_id, prod_data in data.items():
            if prod_data.get("fingerprint") == fingerprint:
                return prod_data
        return None