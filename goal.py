from abc import abstractmethod, ABC
from vector import Vector2
from typing import List
from pathfinding import a_star_pathfind
from skill import skill, support


# an abstract goal class
class Goal(ABC):

    @abstractmethod
    def has_completed(self):
        pass

    @abstractmethod
    def tick_goal(self):
        pass

    @abstractmethod
    def goal_key(self):
        pass

    def cleanup(self):
        pass


class FollowPathGoal(Goal):
    def __init__(self, entity, path: List[Vector2], inaccuracy=1):
        self.path = path
        self.current_target = path.pop()
        self.entity = entity
        self.inaccuracy = inaccuracy

    def has_completed(self):
        return self.path is None or self.current_target is None

    def tick_goal(self):
        # take a step and multiple by maximum speed, then set acceleration
        step = (self.current_target - self.entity.position).normalize()
        self.entity.acceleration = step * self.entity.maximum_speed
        # check if we're close
        if self.entity.position.distance(self.current_target) < self.inaccuracy:
            if self.path:
                self.current_target = self.path.pop()
            else:
                self.current_target = None

    def cleanup(self):
        # reset physics
        self.entity.velocity = self.entity.acceleration = Vector2(0, 0)

    def goal_key(self):
        return "follow_path"


class ShootAtPlayerGoal(Goal):

    def __init__(self, entity, player):
        self.entity = entity
        self.player = player
        self.last_goal = None
        self.tick_count = 0
        self.entity.active_supports = [support.MultipleProjectilesSupport()]
        self.skill = skill.BowAttack()

    def has_completed(self):
        return self.player.health <= 0

    def tick_goal(self):
        # only every 100 ticks to prevent massive spam
        if self.tick_count % 100 == 0:
            # just shoot at them!
            self.skill.use(self.entity.world, self.entity, (self.player.position - self.entity.position).normalize())
        self.tick_count += 1

    def goal_key(self):
        return "attack_player"
