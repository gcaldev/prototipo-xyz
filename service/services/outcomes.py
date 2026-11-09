from dataclasses import dataclass, field


@dataclass
class Outcome:
    allowed: bool
    reason: str
    payload: dict = field(default_factory=dict)
