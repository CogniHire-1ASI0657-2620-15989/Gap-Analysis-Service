from dataclasses import dataclass


@dataclass(frozen=True)
class SkillGap:
    name: str
    skill_type: str
