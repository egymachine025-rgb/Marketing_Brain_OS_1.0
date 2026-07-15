from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from src.models.base import BaseModel

class LayoutType(str, Enum):
    GRID = "GRID"
    LIST = "LIST"
    COLLAPSED = "COLLAPSED"


class ComponentType(str, Enum):
    KPICARD = "KPICARD"
    BAR_CHART = "BAR_CHART"
    LINE_CHART = "LINE_CHART"
    MAP = "MAP"
    TABLE = "TABLE"


@dataclass
class DashboardWidget(BaseModel):
    """
    An individual visual module representation in a layout grid.
    """
    widget_title: str
    component_type: ComponentType
    grid_span_width: int = 4  # Standard columns spanned out of a 12-column template
    raw_visualization_config: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.widget_title.strip():
            raise ValueError("Widget titles require structural text naming patterns.")
        if not (1 <= self.grid_span_width <= 12):
            raise ValueError("Grid span widths must correspond to standard 12-column frameworks (1-12).")


@dataclass
class DashboardModel(BaseModel):
    """
    Container modeling UI arrangement configurations, layout rules, 
    and widget assignments for a specific Dashboard instance.
    """
    dashboard_name: str
    layout_format: LayoutType = LayoutType.GRID
    widgets: list[DashboardWidget] = field(default_factory=list)
    is_public: bool = False

    def __post_init__(self) -> None:
        if not self.dashboard_name.strip():
            raise ValueError("Dashboard instance requires a non-empty name identifier.")