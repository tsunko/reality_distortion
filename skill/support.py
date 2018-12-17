from skill.skill import SkillTag
from typing import List
from abc import ABC, abstractmethod


# base support skill
class Support(ABC):
    def __init__(self, supported_tags: List[SkillTag]):
        self.supported_tags = supported_tags

    # check if we can apply to the skill
    def can_be_applied(self, skill):
        for tag in skill.tags:
            if tag in self.supported_tags:
                return True
        return False

    @abstractmethod
    def apply_effect(self, context):
        pass


class MultipleProjectilesSupport(Support):
    def __init__(self):
        super(MultipleProjectilesSupport, self).__init__([SkillTag.PROJECTILE])

    def apply_effect(self, context):
        context["count"] += 2
        context["damage_modifier"] -= 0.5
        context["spread"] += 7
        return context

    def __str__(self):
        return "Multiple Projectiles"


class SlowerProjectileSupport(Support):
    def __init__(self):
        super(SlowerProjectileSupport, self).__init__([SkillTag.PROJECTILE])

    def apply_effect(self, context):
        context["damage_modifier"] += 0.25
        context["speed"] -= 50
        return context

    def __str__(self):
        return "Slower Projectiles"


class HeavyDrawSupport(Support):
    def __init__(self):
        super(HeavyDrawSupport, self).__init__([SkillTag.PROJECTILE])

    def apply_effect(self, context):
        context["pierce_count"] += 1
        context["speed"] += 100
        context["spread"] += 7
        return context

    def __str__(self):
        return "Heavy Draw"