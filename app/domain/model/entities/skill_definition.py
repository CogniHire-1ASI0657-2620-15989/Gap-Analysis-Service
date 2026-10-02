from dataclasses import dataclass


@dataclass(frozen=True)
class SkillDefinition:
    id: int | None
    name: str
    skill_type: str
    aliases: list[str]
    is_active: bool = True
