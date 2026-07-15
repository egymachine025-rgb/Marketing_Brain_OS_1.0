"""
Onboarding CLI
================
Run this script directly to go through the Mission onboarding flow.
This MUST be the first thing run in the system per NR-002
(Mission Before Product) — no acquisition, research, or strategy code
should run before a Mission exists.

Usage:
    python scripts/onboarding_cli.py
"""

import sys
import os

# Allow running this script directly from the project root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from marketing_brain_os.mission_engine import MissionEngine


def main():
    print("=" * 50)
    print("Marketing Brain OS — Onboarding")
    print("=" * 50)

    engine = MissionEngine()
    mission = engine.run_interactive()

    print("\n--- ملخص الـ Mission ---")
    print(f"الهدف: {mission['goal']}")
    print(f"مستوى الخبرة: {mission['user']['experience_level']}")
    print(f"المصادر: {mission['resources']['sources']}")
    print(f"أدوات البيع: {mission['sales_tools']}")
    print(f"الميزانية: {mission['budget']} (صفر تمويل: {mission['constraints']['zero_funding']})")


if __name__ == "__main__":
    main()
