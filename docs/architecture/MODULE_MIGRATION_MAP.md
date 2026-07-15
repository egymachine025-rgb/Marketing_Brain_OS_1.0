# Module Migration Mapping Schema: Marketing Brain OS 1.0
**Status:** READY FOR EXECUTION  
**Target Architecture:** clean domain-driven architecture (`src/`)

This specification details the structural translation of individual MVP processing modules from `marketing_brain_os/` to their final consolidated destinations in `src/`.

---

## 1. Migration Map Matrix

| Source Module | Target `src/` Path | Architectural Layer | Architectural Role |
| :--- | :--- | :--- | :--- |
| **`product.py`** | `src/models/product.py` | **Domain Layer** (Core Models) | Unifies core entity definitions; inherits from `src/models/base.py` for standard dynamic serialization and schema validation. |
| **`product_builder.py`** | `src/core/product_builder.py` | **Domain Services Layer** (Factories) | Factory service that translates raw parsing results and source telemetry into valid `Product` entities. |
| **`normalizer.py`** | `src/core/normalizer.py` | **Domain Services Layer** (Logic) | Standardizes variations in typography, metrics, values, and currencies into clean, uniform values. |
| **`fingerprint_engine.py`** | `src/core/fingerprint_engine.py` | **Domain Services Layer** (Hashing) | Generates deterministic SHA-256 signatures to identify unique content configurations. |
| **`duplicate_engine.py`** | `src/core/duplicate_engine.py` | **Domain Services Layer** (Rules) | Evaluates uniqueness matches on incoming items against stored product repositories. |
| **`parser_manager.py`** | `src/parsers/parser_manager.py` | **Infrastructure Layer** (Parsers) | Orchestration facade managing the linear ingestion pipeline across individual string extraction sub-parsers. |

---

## 2. Dependency Alignment Rules

To prevent dependency cycles and maintain a strict inward-pointing architecture:

1. **Entities (`src/models/`)** must never import from `src/core/`, `src/parsers/`, or external infrastructure components. They depend only on `src/models/base.py` and standard library components.
2. **Domain Services (`src/core/`)** can import domain entities (`src/models/`) and abstract repositories, but cannot depend on concrete parser or controller frameworks.
3. **Parsers (`src/parsers/`)** exist as parsing components in the infrastructure loop. They yield DTO structures (such as `ParseResult`) which are then converted to domain models using `ProductBuilder`.