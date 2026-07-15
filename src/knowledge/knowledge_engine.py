"""
Marketing Brain OS
Knowledge Engine
"""

from app.knowledge.knowledge_object import KnowledgeObject
from app.knowledge.knowledge_repository import KnowledgeRepository


class KnowledgeEngine:

    def __init__(self):

        self.repository = KnowledgeRepository()

    def learn(
        self,
        knowledge: KnowledgeObject,
    ):

        existing = self.repository.load(
            knowledge.id
        )

        if existing is None:

            self.repository.save(knowledge)

            return knowledge

        # -------------------------
        # Merge
        # -------------------------

        existing.confidence = max(

            existing.confidence,

            knowledge.confidence,

        )

        existing.update()

        self.repository.save(existing)

        return existing

    def remember(
        self,
        knowledge_list: list[KnowledgeObject],
    ):

        result = []

        for knowledge in knowledge_list:

            result.append(

                self.learn(
                    knowledge
                )

            )

        return result

    def get(self, knowledge_id: str):

        return self.repository.load(
            knowledge_id
        )

    def all(self):

        return self.repository.all()

    def count(self):

        return len(

            self.repository.all()

        )
}