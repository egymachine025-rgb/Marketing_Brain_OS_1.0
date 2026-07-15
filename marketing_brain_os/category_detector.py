from __future__ import annotations

class CategoryDetector:
    """
    Standardizes varied multi-lingual keywords into normalized product taxonomies.
    """

    def __init__(self) -> None:
        pass

    def detect(self, text: str) -> str:
        """
        Analyzes raw text for specific Arabic and English identifiers to return normalized categories.
        """
        if not text:
            return "Other"
            
        clean = text.lower()
        
        # 1. Accessories, Watches, Eyewear, Bags, Shoes (High precision leaf nodes)
        if any(k in clean for k in ["ساعة", "watch"]):
            return "Watch"
        if any(k in clean for k in ["نظارة", "eyewear", "glasses", "sunglasses"]):
            return "Eyewear"
        if any(k in clean for k in ["شنطة", "حقيبة", "محفظة", "bag", "handbag", "wallet"]):
            return "Bags"
        if any(k in clean for k in ["حذاء", "سنيكرز", "بوت", "shoes", "sneakers", "boots"]):
            return "Shoes"
        if any(k in clean for k in ["إكسسوارات", "اكسسوارات", "accessories", "accessory"]):
            return "Accessories"
            
        # 2. Demographic Parsing
        is_kids = any(k in clean for k in ["أطفال", "اطفال", "kids", "baby", "children"])
        is_women = any(k in clean for k in ["حريمي", "نسائي", "women", "ladies", "lady", "عباية", "فستان", "تنورة", "حجاب", "abaya", "dress", "skirt", "hijab"])
        is_men = any(k in clean for k in ["رجالي", "men", "mens", "man"])

        # 3. Clothing Triggers Check
        clothing_triggers = [
            "ملابس", "تيشيرت", "بولو", "قميص", "بنطلون", "جينز", "شورت", "جاكيت", "هودي", "سويت شيرت",
            "clothing", "t-shirt", "polo", "shirt", "pants", "jeans", "shorts", "jacket", "hoodie", "sweatshirt"
        ]
        has_clothing = any(k in clean for k in clothing_triggers) or is_women or is_men or is_kids

        if has_clothing:
            if is_kids:
                return "Kids Clothing"
            if is_women:
                return "Women Clothing"
            if is_men or any(k in clean for k in ["رجالي", "بولو", "polo"]):
                return "Men Clothing"
            return "Clothing"
            
        return "Other"