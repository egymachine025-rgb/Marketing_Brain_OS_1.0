"""
Knowledge Base
"""

from app.knowledge.knowledge_object import KnowledgeObject


class KnowledgeBase:

    def __init__(self):

        self.items: list[KnowledgeObject] = []

    def add(self, knowledge: KnowledgeObject):

        self.items.append(knowledge)

    def all(self):

        return self.items

    def count(self):

        return len(self.items)