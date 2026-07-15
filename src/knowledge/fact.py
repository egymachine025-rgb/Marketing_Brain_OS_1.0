"""
Knowledge Fact
"""

from dataclasses import dataclass


@dataclass
class Fact:

    subject: str

    predicate: str

    value: str