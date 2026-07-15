from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from src.models.base import BaseModel
from src.models.mission import Mission
from src.models.goal import Goal
from src.models.resource import Resource
from src.models.constraint import Constraint

@dataclass
class BusinessContext(BaseModel):
    organization_name: str
    company_mission: Mission = field(default_factory=lambda: Mission(statement="UNKNOWN", vision="UNKNOWN"))
    active_goals: list[Goal] = field(default_factory=list)
    available_resources: list[Resource] = field(default_factory=list)
    operational_constraints: list[Constraint] = field(default_factory=list)
    market_ids: list[uuid.UUID] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.organization_name.strip():
            raise ValueError("Business context must resolve to a valid organization name.")