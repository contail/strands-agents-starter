from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class TwinState:
    """Simple digital twin state entity.

    In a real system, split into value objects and entities with invariants and
    domain services as needed.
    """

    name: str
    properties: Dict[str, Any] = field(default_factory=dict)

    def update(self, **changes: Any) -> None:
        self.properties.update(changes)

    def snapshot(self) -> Dict[str, Any]:
        return {"name": self.name, **self.properties}


