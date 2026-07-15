"""
Marketing Brain OS
==================

Pure Python marketing intelligence system.
No AI dependencies. No external service dependencies.

LAYER 1 — PARSER:
    - TextCleaner, LanguageDetector, BrandDetector, CategoryDetector,
      PriceExtractor, OfferExtractor, KeywordExtractor, FeatureExtractor,
      ColorExtractor, ParserManager

LAYER 2 — RESEARCH:
    - MarketAnalyzer, AudienceAnalyzer, TrendAnalyzer, CompetitorAnalyzer,
      ResearchManager

LAYER 3 — MISSION:
    - MissionBuilder, MissionValidator, MissionRepository, MissionEngine

LAYER 1b — ACQUISITION:
    - AcquisitionConfig, ScanState, TelegramAcquisition

LAYER 2b — PRODUCT PIPELINE:
    - Product, ProductBuilder, ProductNormalizer, FingerprintEngine,
      MediaRepository, RawRepository

====================================================================
!! DO NOT replace this file with a version that does plain top-level
   `from .module import Class` statements for every module listed
   above. !!

   Several modules are still empty placeholder files (implementation
   pending). A plain top-level import crashes THIS ENTIRE PACKAGE the
   moment Python loads it — including modules that ARE finished and
   working (e.g. mission_engine, product_builder), because Python
   always executes __init__.py before any submodule of the package.

   This has already happened once (this file was reverted to the
   crashing version on 2026-07-14, which took down every finished
   module and every test in tests/ at once).

   Each import below is attempted individually via _try_import() and
   skipped if the module isn't implemented yet, instead of crashing
   the whole package. Run:
       python -c "import marketing_brain_os as m; m.print_status()"
   to see what's implemented vs still a placeholder.

   Only replace this pattern once EVERY module below is actually
   implemented (i.e. __missing__ is empty) — at that point a plain
   import list is fine and this whole safety mechanism can be deleted.
====================================================================
"""

__version__ = "2.1.0"
__author__ = "Marketing Brain OS"

__available__: list[str] = []
__missing__: list[str] = []


def _try_import(module_name: str, class_name: str) -> None:
    """Import class_name from .module_name into this package's namespace.
    On any failure (empty file, missing class, syntax error), record it
    in __missing__ and move on instead of crashing the whole package."""
    import importlib

    try:
        module = importlib.import_module(f".{module_name}", package=__name__)
        globals()[class_name] = getattr(module, class_name)
        __available__.append(class_name)
    except Exception as e:
        __missing__.append(f"{class_name} ({type(e).__name__}: {e})")


# Layer 1: Parser
_try_import("text_cleaner", "TextCleaner")
_try_import("language_detector", "LanguageDetector")
_try_import("brand_detector", "BrandDetector")
_try_import("category_detector", "CategoryDetector")
_try_import("price_extractor", "PriceExtractor")
_try_import("offer_extractor", "OfferExtractor")
_try_import("keyword_extractor", "KeywordExtractor")
_try_import("feature_extractor", "FeatureExtractor")
_try_import("color_extractor", "ColorExtractor")
_try_import("parser_manager", "ParserManager")

# Layer 2: Research
_try_import("market_analyzer", "MarketAnalyzer")
_try_import("audience_analyzer", "AudienceAnalyzer")
_try_import("trend_analyzer", "TrendAnalyzer")
_try_import("competitor_analyzer", "CompetitorAnalyzer")
_try_import("research_manager", "ResearchManager")

# Layer 3: Mission
_try_import("mission_builder", "MissionBuilder")
_try_import("mission_validator", "MissionValidator")
_try_import("mission_repository", "MissionRepository")
_try_import("mission_engine", "MissionEngine")

# Layer 1b: Acquisition
_try_import("telegram_acquisition", "AcquisitionConfig")
_try_import("telegram_acquisition", "ScanState")
_try_import("telegram_acquisition", "TelegramAcquisition")

# Layer 2b: Product pipeline
_try_import("product", "Product")
_try_import("product_builder", "ProductBuilder")
_try_import("normalizer", "ProductNormalizer")
_try_import("fingerprint_engine", "FingerprintEngine")
_try_import("media_repository", "MediaRepository")
_try_import("raw_repository", "RawRepository")


def print_status() -> None:
    """Quick sanity check: run
        python -c "import marketing_brain_os as m; m.print_status()"
    to see what's implemented vs still a placeholder/broken."""
    print("Available:", ", ".join(__available__) or "(none)")
    print("Missing / broken:")
    for item in __missing__:
        print(" -", item)
    if not __missing__:
        print(" (none)")