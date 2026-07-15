from __future__ import annotations

class BrandDetector:
    """
    Deterministic, dictionary-based brand matching engine supporting 
    both English and Arabic transliterations.
    """

    def __init__(self) -> None:
        # Dictionary mapping lowercase keys to canonical brand names
        self.brand_mappings = {
            # Lacoste
            "lacoste": "Lacoste", "لاكوست": "Lacoste",
            # Nike
            "nike": "Nike", "نايك": "Nike", "نايكي": "Nike",
            # Adidas
            "adidas": "Adidas", "اديداس": "Adidas", "أديداس": "Adidas",
            # Puma
            "puma": "Puma", "بوما": "Puma",
            # Zara
            "zara": "Zara", "زارا": "Zara",
            # H&M
            "h&m": "H&M", "h and m": "H&M", "اتش اند ام": "H&M", "اتش أند ام": "H&M",
            # LC Waikiki
            "lc waikiki": "LC Waikiki", "lcwaikiki": "LC Waikiki", "waikiki": "LC Waikiki", "ال سي وايكيكي": "LC Waikiki", "وايكيكي": "LC Waikiki",
            # Defacto
            "defacto": "Defacto", "ديفاكتو": "Defacto", "دي فاكتو": "Defacto",
            # American Eagle
            "american eagle": "American Eagle", "امريكان ايجل": "American Eagle", "أمريكان إيجل": "American Eagle",
            # Tommy Hilfiger
            "tommy hilfiger": "Tommy Hilfiger", "tommy": "Tommy Hilfiger", "تومي": "Tommy Hilfiger", "تومي هيلفيغر": "Tommy Hilfiger", "تومي هيلفيجر": "Tommy Hilfiger",
            # Calvin Klein
            "calvin klein": "Calvin Klein", "ck": "Calvin Klein", "كالفن كلاين": "Calvin Klein",
            # Levi's
            "levi's": "Levi's", "levis": "Levi's", "ليفايس": "Levi's", "ليفايز": "Levi's",
            # Skechers
            "skechers": "Skechers", "سكتشرز": "Skechers", "اسكيتشرز": "Skechers",
            # New Balance
            "new balance": "New Balance", "نيو بالانس": "New Balance", "نيوبالانس": "New Balance",
            # Converse
            "converse": "Converse", "كونفرس": "Converse",
            # Vans
            "vans": "Vans", "فانز": "Vans",
            # Gucci
            "gucci": "Gucci", "قوتشي": "Gucci", "جوتشي": "Gucci",
            # Prada
            "prada": "Prada", "برادا": "Prada",
            # Dior
            "dior": "Dior", "ديور": "Dior",
            # Louis Vuitton
            "louis vuitton": "Louis Vuitton", "vuitton": "Louis Vuitton", "لويس فيتون": "Louis Vuitton", "لويس فوتون": "Louis Vuitton",
        }

    def detect(self, text: str) -> str:
        """
        Scans raw text to match canonical brands without relying on heavy NLP frameworks.
        """
        if not text:
            return "Unknown"
        
        clean_text = text.lower()
        
        # Sort keys by length descending to match multi-word brands (e.g., "new balance") before single ones
        sorted_keys = sorted(self.brand_mappings.keys(), key=len, reverse=True)
        for key in sorted_keys:
            if key in clean_text:
                return self.brand_mappings[key]
                
        return "Unknown"