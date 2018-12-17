from world.world import World
from entity import Entity, ArrowEntity
from enum import Enum
from typing import List
from abc import abstractmethod, ABC
from vector import Vector2
from random import randint


class SkillTag(Enum):
    MELEE = 0
    PROJECTILE = 1
    SPELL = 2


class Skill(ABC):
    def __init__(self, name: str, tags: List[SkillTag]):
        self.name = name
        self.tags = tags

    @abstractmethod
    def use(self, world: World, source: Entity, direction: Vector2):
        pass


class BowAttack(Skill):
    def __init__(self):
        super(BowAttack, self).__init__("Barrage", [SkillTag.PROJECTILE])

    def use(self, world: World, source: Entity, direction: Vector2):
        context = self.generate_context(source)
        to_spawn = context["count"]
        while to_spawn > 0:
            # generate slightly random direction to allow spread
            slightly_random_direction = direction + Vector2(randint(-context["spread"], context["spread"]) / 20,
                                                            randint(-context["spread"], context["spread"]) / 20)
            # world, position, maximum_speed, damage, source
            arrow = ArrowEntity(world, source.position, context["speed"], slightly_random_direction,
                                400 * context["damage_modifier"], source, context["pierce_count"])
            # spawn "entity" and subtract from to_spawn
            world.entities.append(arrow)
            to_spawn -= 1

    def generate_context(self, source: Entity):
        # base context for applying supports to
        context = {
            "damage_modifier": 1,
            "count": 1,
            "pierce_count": 0,
            "speed": 100,
            "spread": 1
        }
        # apply any active supports
        for support in source.active_supports:
            context = support.apply_effect(context)
        return context
