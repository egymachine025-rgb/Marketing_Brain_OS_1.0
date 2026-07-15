# Architectural Audit & Migration Plan: Marketing Brain OS 1.0
**Owner:** Senior Software Engineer  
**Sprint:** MVP-001  
**Status:** APPROVED  

---

## 1. Executive Summary

During the rapid development of MVP-001, two structural layouts emerged:
1. `src/`: Designed around strict clean architecture principles, containing abstract domain models, asynchronous port interfaces (repositories), the platform-specific acquisition layer, and the core MVP ingestion pipeline.
2. `marketing_brain_os/`: Developed as a localized, functional workspace containing data normalization engines, deterministic regex parsers, and product-building factories.

This document establishes the migration protocol to merge `marketing_brain_os/` into the consolidated `src/` ecosystem, establishing a single source of truth without modifying operational logic.

---

## 2. Component Reconciliation Matrix

### A. Duplicated Modules (Conflict Resolution)
These components exist in both directories and must be merged to resolve structural type mismatch issues:

| Module | `marketing_brain_os/` Location | `src/` Location | Resolution Plan |
| :--- | :--- | :--- | :--- |
| **Product Model** | `product.py` (Extended MVP Model) | `models/product.py` (Original Core Model) | **Merge into `src/models/product.py`**. Keep the extended attributes required by `TASK-G003` (such as `fingerprint`, `brand`, `colors`, `features`, `telegram_message_id`, etc.) while ensuring it continues to inherit from `src/models/base.py` for dynamic `to_dict` serialization. |

---

### B. Modules to Keep (Untouched)
These modules are structurally sound, decoupled, and will remain in their current locations within the `src/` hierarchy:

*   **Core Base Engine:** `src/models/base.py` (Contains serialization logic, metadata, and core Enums)
*   **Domain Schemas:** 
    *   `src/models/market.py`
    *   `src/models/audience.py`
    *   `src/models/competitor.py`
    *   `src/models/supplier.py`
    *   `src/models/trend.py`
    *   `src/models/campaign.py`
    *   `src/models/decision.py`
    *   `src/models/analysis.py`
    *   `src/models/folder.py`
    *   `src/models/snapshots.py`
    *   `src/models/research_report.py`
    *   `src/models/mission.py`
    *   `src/models/goal.py`
    *   `src/models/resource.py`
    *   `src/models/constraint.py`
    *   `src/models/business_context.py`
*   **Acquisition Interfaces:** `src/acquisition/` (All files: `base`, `telegram`, `facebook`, `instagram`, `youtube`, `tiktok`, `websites`)
*   **Repository Interfaces:** `src/repositories/` (All files: `base`, `product`, `market`, `audience`, `trend`, `analysis`, `decision`, `knowledge`, `dashboard`, `factory`)
*   **Orchestration Engine:** `src/core/pipeline.py` & `src/core/pipeline_result.py`

---

### C. Modules to Migrate (Relocate & Integrate)
These modules represent valuable parser, builder, and normalizer engines that currently sit in the legacy folder. They will be relocated into cohesive directories within `src/`:

| Original Location | Target `src/` Destination | Classification | Role |
| :--- | :--- | :--- | :--- |
| `marketing_brain_os/text_cleaner.py` | `src/parsers/text_cleaner.py` | Infrastructure | Sanitization of inputs |
| `marketing_brain_os/brand_detector.py` | `src/parsers/brand_detector.py` | Infrastructure | Regex brand parsing |
| `marketing_brain_os/category_detector.py` | `src/parsers/category_detector.py` | Infrastructure | Category classification |
| `marketing_brain_os/price_extractor.py` | `src/parsers/price_extractor.py` | Infrastructure | Price-to-float extraction |
| `marketing_brain_os/offer_extractor.py` | `src/parsers/offer_extractor.py` | Infrastructure | Discount & promo parsing |
| `marketing_brain_os/keyword_extractor.py` | `src/parsers/keyword_extractor.py` | Infrastructure | Semantic keyword metrics |
| `marketing_brain_os/feature_extractor.py` | `src/parsers/feature_extractor.py` | Infrastructure | Spec extraction |
| `marketing_brain_os/color_extractor.py` | `src/parsers/color_extractor.py` | Infrastructure | Design color parsing |
| `marketing_brain_os/parser_manager.py` | `src/parsers/parser_manager.py` | Infrastructure | Central parsing facade |
| `marketing_brain_os/product_builder.py` | `src/core/product_builder.py` | Domain Services | Product factory constructor |
| `marketing_brain_os/normalizer.py` | `src/core/normalizer.py` | Domain Services | Data standardization and unit scaling |

---

### D. Modules to Delete
Once the migration is complete, the legacy root folder must be removed:

*   `marketing_brain_os/` directory (Delete completely once all files are successfully merged/migrated to `src/`).

---

## 3. Targeted Clean Architecture Dependency Graph

Below is the clean architecture dependency flow for the unified system, showcasing how layers depend strictly inward toward core domain structures:
---

## 4. Phase-Based Migration Order

To ensure zero downtime and prevent broken import references, execution of this migration plan must follow this exact order:

### Phase 1: Models Consolidation & Base Alignment
1. **Sync Product Models:** Update `src/models/product.py` to include all fields from `marketing_brain_os/product.py` while retaining its inheritance from `src/models/base.py`.
2. **Type-Check Models:** Ensure all tests inside `tests/` pass against the consolidated core dataclass.

### Phase 2: Relocate Processing Infrastructure
1. **Create Directories:** Confirm directories `src/parsers/` and `src/core/` are initialized.
2. **Move Parsers:** Move `text_cleaner.py`, `brand_detector.py`, `category_detector.py`, `price_extractor.py`, `offer_extractor.py`, `keyword_extractor.py`, `feature_extractor.py`, `color_extractor.py`, and `parser_manager.py` into `src/parsers/`.
3. **Move Core Services:** Move `product_builder.py` and `normalizer.py` into `src/core/`.

### Phase 3: Update Imports & Namespace Resolution
1. **Standardize Internal Imports:** Modify import lines across the parser and normalizer files to reference their new paths within `src/` (e.g., `from src.models.base import Currency` instead of legacy relative routes).
2. **Pipeline Re-mapping:** Update `src/core/pipeline.py` to import modules from their new consolidated namespaces:
   * `from src.parsers.parser_manager import ParserManager`
   * `from src.core.product_builder import ProductBuilder`
   * `from src.core.normalizer import ProductNormalizer`

### Phase 4: Test Suite Synchronization & Verification
1. **Relocate Tests:** Move and update the imports within your unit tests to match:
   * `tests/test_product_builder.py` -> Update imports to point to `src/core/product_builder`
   * `tests/test_normalizer.py` -> Update imports to point to `src/core/normalizer`
2. **Execute Full Suite:** Run `python -m unittest discover -s tests` to ensure all tests pass cleanly.

### Phase 5: Cleanup
1. **Deprecate Legacy Workspace:** Delete the empty `marketing_brain_os/` directory.