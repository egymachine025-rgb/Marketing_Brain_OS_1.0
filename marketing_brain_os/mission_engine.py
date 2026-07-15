"""
Mission Engine Module
========================
Orchestrates the full Mission lifecycle: ask onboarding questions (or
accept answers programmatically) -> build -> validate -> save.

This is the entry point of Marketing Brain OS. Per NR-002 (Mission
Before Product), no other layer should be invoked until
MissionEngine.run_interactive() (or .intake()) has produced a valid,
saved Mission.

No AI. Pure Python.
"""

from __future__ import annotations
from typing import Any

from marketing_brain_os.mission_builder import MissionBuilder
from marketing_brain_os.mission_validator import MissionValidator
from marketing_brain_os.mission_repository import MissionRepository


# The four onboarding questions, in order. Each option's "value" is what
# gets passed to MissionBuilder — the "label" is what a human reads.
ONBOARDING_QUESTIONS: list[dict[str, Any]] = [
    {
        "id": "goal",
        "prompt": "إيه هدفك من استخدام البرنامج؟",
        "type": "single",
        "options": [
            {"value": "sell_existing_product", "label": "بيع منتج/خدمة عندي بالفعل (زي قناة تيليجرام)"},
            {"value": "affiliate_marketing", "label": "تسويق بالعمولة لمنتجات مش ملكي"},
            {"value": "build_audience_first", "label": "بناء جمهور/محتوى قبل تحديد المنتج"},
        ],
    },
    {
        "id": "experience_level",
        "prompt": "عندك خبرة سابقة في التسويق أو البيع أونلاين؟",
        "type": "single",
        "options": [
            {"value": "beginner", "label": "لأ، مبتدئ"},
            {"value": "experienced", "label": "أيوه، عندي خبرة"},
        ],
    },
    {
        "id": "sources",
        "prompt": "إيه المصادر المتاحة عندك دلوقتي؟ (تقدر تختار أكتر من واحد)",
        "type": "multi",
        "options": [
            {"value": "telegram_channel", "label": "قناة تيليجرام"},
            {"value": "facebook_page", "label": "صفحة فيسبوك"},
            {"value": "instagram_page", "label": "صفحة انستجرام"},
            {"value": "tiktok_account", "label": "حساب تيك توك"},
            {"value": "website", "label": "موقع إلكتروني"},
            {"value": "none_yet", "label": "لسه مفيش"},
        ],
    },
    {
        "id": "sales_tools",
        "prompt": "إيه أدوات البيع المتاحة عندك؟ (تقدر تختار أكتر من واحد)",
        "type": "multi",
        "options": [
            {"value": "manual_reply", "label": "رد يدوي على الرسايل"},
            {"value": "chatbot", "label": "شات بوت"},
            {"value": "payment_link", "label": "رابط دفع أونلاين"},
            {"value": "delivery_company", "label": "شركة توصيل"},
            {"value": "none_yet", "label": "لسه مفيش نظام منظم"},
        ],
    },
]


class MissionEngine:
    """Orchestrates onboarding: collect answers, build, validate, persist."""

    def __init__(
        self,
        builder: MissionBuilder | None = None,
        validator: MissionValidator | None = None,
        repository: MissionRepository | None = None,
    ):
        self.builder = builder or MissionBuilder()
        self.validator = validator or MissionValidator()
        self.repository = repository or MissionRepository()

    def intake(self, answers: dict[str, Any]) -> dict[str, Any]:
        """
        Programmatic entry point: pass raw answers directly (e.g. from a
        web form or API call) and get back a saved, validated Mission.

        Raises ValueError if the Mission fails validation.
        """
        mission = self.builder.build(answers)
        result = self.validator.validate(mission)
        if not result.is_valid:
            raise ValueError(
                "Mission failed validation:\n- " + "\n- ".join(result.errors)
            )
        return self.repository.save(mission)

    def run_interactive(self) -> dict[str, Any]:
        """
        CLI entry point: ask the onboarding questions in the terminal,
        collect answers, and produce a saved Mission.
        """
        answers: dict[str, Any] = {}

        for question in ONBOARDING_QUESTIONS:
            answers[question["id"]] = self._ask(question)

        print("\nهل عندك وصف مختصر للمنتج أو المشروع؟ (اختياري، اضغط Enter للتخطي)")
        answers["business_description"] = input("> ").strip()

        print("\nهل فيه ميزانية متاحة؟ اكتب رقم، أو 0 لو البداية بصفر تمويل")
        budget_raw = input("> ").strip()
        answers["budget"] = float(budget_raw) if budget_raw else 0

        mission = self.intake(answers)
        print(f"\n✔ تم حفظ الـ Mission بنجاح. ID: {mission['id']}")
        return mission

    def _ask(self, question: dict[str, Any]) -> Any:
        print(f"\n{question['prompt']}")
        for i, option in enumerate(question["options"], start=1):
            print(f"  {i}. {option['label']}")

        if question["type"] == "single":
            choice = self._read_index(len(question["options"]))
            return question["options"][choice - 1]["value"]

        # multi-select: comma separated indices, e.g. "1,3"
        print("  (تقدر تختار أكتر من رقم، مفصولين بفاصلة، زي: 1,3)")
        raw = input("> ").strip()
        indices = [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]
        selected = [
            question["options"][i - 1]["value"]
            for i in indices
            if 1 <= i <= len(question["options"])
        ]
        return selected

    def _read_index(self, max_value: int) -> int:
        while True:
            raw = input("> ").strip()
            if raw.isdigit() and 1 <= int(raw) <= max_value:
                return int(raw)
            print(f"اختر رقم من 1 لـ {max_value}")
