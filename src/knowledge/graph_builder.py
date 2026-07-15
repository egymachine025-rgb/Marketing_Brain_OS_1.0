from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Any

from contracts.knowledge_graph_contract import KnowledgeGraphContract
from contracts.knowledge_repository_contract import KnowledgeRepositoryContract
from marketing_brain_os.product import Product
from src.knowledge.knowledge_object import KnowledgeObject


class GraphBuilder:
    """
    Builds knowledge graph relationships by extracting entity signals
    from product records and saving both objects and relationships.
    """

    PRICE_TIERS = [
        (50.0, "budget"),
        (200.0, "midrange"),
        (500.0, "premium"),
    ]

    def build_from_products(
        self,
        products: list[Product],
        repository: KnowledgeRepositoryContract,
        graph: KnowledgeGraphContract,
    ) -> None:
        product_entities: dict[str, KnowledgeObject] = {}
        category_groups: dict[str, list[Product]] = defaultdict(list)

        for product in products:
            product_entities[str(product.id)] = self._build_product_graph(product, repository, graph)
            category_key = product.category.strip().lower()
            category_groups[category_key].append(product)

        self._link_similar_products(category_groups, product_entities, graph)

    def _build_product_graph(
        self,
        product: Product,
        repository: KnowledgeRepositoryContract,
        graph: KnowledgeGraphContract,
    ) -> KnowledgeObject:
        brand_node = self._ensure_entity(
            repository,
            "brand",
            product.brand,
            product.brand,
            product.language,
            {"source_product_id": str(product.id)},
        )

        category_node = self._ensure_entity(
            repository,
            "category",
            product.category,
            product.category,
            product.language,
            {"source_product_id": str(product.id)},
        )
        graph.add_relationship(brand_node.id, category_node.id, "has_category")

        market_name = self._extract_market(product)
        if market_name:
            market_node = self._ensure_entity(
                repository,
                "market",
                market_name,
                market_name,
                product.language,
                {"source_product_id": str(product.id)},
            )
            graph.add_relationship(brand_node.id, market_node.id, "has_market")

        tier_name = self._infer_tier(product.price)
        tier_node = self._ensure_entity(
            repository,
            "tier",
            tier_name,
            tier_name,
            product.language,
            {"confidence_bucket": tier_name},
        )
        graph.add_relationship(brand_node.id, tier_node.id, "has_tier")

        product_node = self._ensure_entity(
            repository,
            "product",
            product.name,
            product.description or product.offer or product.name,
            product.language,
            {
                "product_id": str(product.id),
                "brand": product.brand,
                "category": product.category,
                "price": product.price,
                "currency": getattr(product.currency, "value", str(product.currency)),
                "market": market_name,
            },
        )

        self._connect_features(product, repository, graph, product_node)
        self._connect_audiences(product, repository, graph, brand_node, product_node)

        return product_node

    def _connect_features(
        self,
        product: Product,
        repository: KnowledgeRepositoryContract,
        graph: KnowledgeGraphContract,
        product_node: KnowledgeObject,
    ) -> None:
        for feature in product.features or []:
            normalized = str(feature).strip()
            if not normalized:
                continue
            feature_node = self._ensure_entity(
                repository,
                "feature",
                normalized,
                normalized,
                product.language,
                {"source_product_id": str(product.id)},
            )
            graph.add_relationship(product_node.id, feature_node.id, "has_feature")

    def _connect_audiences(
        self,
        product: Product,
        repository: KnowledgeRepositoryContract,
        graph: KnowledgeGraphContract,
        brand_node: KnowledgeObject,
        product_node: KnowledgeObject,
    ) -> None:
        for audience in self._extract_audience(product):
            audience_node = self._ensure_entity(
                repository,
                "audience",
                audience,
                audience,
                product.language,
                {"source_product_id": str(product.id)},
            )
            graph.add_relationship(brand_node.id, audience_node.id, "has_audience")
            graph.add_relationship(product_node.id, audience_node.id, "has_audience")

    def _ensure_entity(
        self,
        repository: KnowledgeRepositoryContract,
        entity_type: str,
        name: str,
        value: Any,
        language: str,
        metadata: dict[str, Any] | None = None,
    ) -> KnowledgeObject:
        existing = repository.get_by_type_and_name(entity_type, name, language)
        metadata = dict(metadata or {})
        knowledge = KnowledgeObject(
            type=entity_type,
            name=name,
            value=value,
            source="graph_builder",
            confidence=0.95,
            language=language,
            metadata=metadata,
        )
        return repository.save(knowledge)

    def _link_similar_products(
        self,
        category_groups: dict[str, list[Product]],
        product_entities: dict[str, KnowledgeObject],
        graph: KnowledgeGraphContract,
    ) -> None:
        for products in category_groups.values():
            for left, right in combinations(products, 2):
                if self._is_similar(left, right):
                    left_entity = product_entities[str(left.id)]
                    right_entity = product_entities[str(right.id)]
                    weight = self._similarity_weight(left.price, right.price)
                    graph.add_relationship(
                        left_entity.id,
                        right_entity.id,
                        "similar_to",
                        weight=weight,
                        metadata={"category": left.category},
                    )
                    graph.add_relationship(
                        right_entity.id,
                        left_entity.id,
                        "similar_to",
                        weight=weight,
                        metadata={"category": right.category},
                    )

    def _extract_market(self, product: Product) -> str | None:
        if getattr(product, "market", None):
            return str(product.market).strip()
        if getattr(product, "country", None):
            return str(product.country).strip()
        if getattr(product, "attributes", None):
            for key in ("market", "country", "region"):
                value = product.attributes.get(key)
                if value:
                    return str(value).strip()
        return None

    def _extract_audience(self, product: Product) -> list[str]:
        audiences: list[str] = []
        if getattr(product, "attributes", None):
            raw = product.attributes.get("audience")
            if raw:
                audiences.extend([item.strip() for item in str(raw).split(",") if item.strip()])

        for tag in getattr(product, "tags", []) or []:
            normalized = str(tag).strip()
            if normalized.lower() in {"men", "women", "unisex", "18-35", "18-24", "25-34"}:
                audiences.append(normalized)

        return list(dict.fromkeys([audience for audience in audiences if audience]))

    def _infer_tier(self, price: float) -> str:
        for threshold, tier in self.PRICE_TIERS:
            if price < threshold:
                return tier
        return "luxury"

    def _is_similar(self, left: Product, right: Product) -> bool:
        if left.category.strip().lower() != right.category.strip().lower():
            return False
        if left.price <= 0 or right.price <= 0:
            return False
        ratio = abs(left.price - right.price) / max(left.price, right.price)
        return ratio <= 0.25

    def _similarity_weight(self, left_price: float, right_price: float) -> float:
        if left_price <= 0 or right_price <= 0:
            return 0.0
        ratio = abs(left_price - right_price) / max(left_price, right_price)
        return round(max(0.0, 1.0 - ratio), 4)
