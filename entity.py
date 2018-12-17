from vector import Vector2
from shape import Rectangle
import goal

HALF = Vector2(0.5, 0.5)


# calculates velocity of entity with respect to a maximum speed
def _entity_calculate_velocity(acceleration: Vector2, current_velocity: Vector2, maximum: Vector2):
    new_velocity = current_velocity + acceleration
    new_velocity.x = min(new_velocity.x, maximum.x)
    new_velocity.y = min(new_velocity.y, maximum.y)
    return new_velocity


# base of a body with physics
class PhysicsBody:
    def __init__(self, position=Vector2(0, 0), maximum_speed=100, drag=0.9, size=Vector2(10, 10)):
        self.position = position
        self.acceleration = self.velocity = Vector2(0, 0)
        self.maximum_speed = Vector2(maximum_speed, maximum_speed)
        self.drag = Vector2(drag, drag)
        self.size = size

    def tick_physics(self, dt):
        old_velocity = self.velocity.clone()
        new_velocity = _entity_calculate_velocity(self.acceleration, old_velocity, self.maximum_speed)
        self.position += ((old_velocity + new_velocity) * HALF) * Vector2(dt, dt)


# base entity
class Entity(PhysicsBody):
    def __init__(self, world, position=Vector2(0, 0), maximum_speed=100, drag=0.85, maximum_health=1000):
        super(Entity, self).__init__(position, maximum_speed, drag=drag)
        self.world = world
        self.goals = dict()
        self.health = self.maximum_health = maximum_health
        self.color = (255, 255, 255)
        self.planning = None
        self.active_supports = list()

    def tick_entity(self, dt):
        # tick all of their objectives and cleanup if they're done
        for key, goal in dict(self.goals).items():
            goal.tick_goal()
            if goal.has_completed():
                goal.cleanup()
                del self.goals[key]
        # tick physics
        self.tick_physics(dt)

    # use goal_key to avoid duplicate goals
    def add_goal(self, goal):
        self.goals[goal.goal_key()] = goal

    # instruct to follow path IF path exists
    def follow_path(self, path):
        if path:
            path_goal = goal.FollowPathGoal(self, path)
            self.add_goal(path_goal)

    # adds or removes a support if it exists or not
    def toggle_support(self, support):
        index = -1
        for i in range(len(self.active_supports)):
            if isinstance(self.active_supports[i], type(support)):
                index = i
                break
        if index == -1:
            self.active_supports.append(support)
        else:
            self.active_supports.pop(index)
        return False


# base EnemyEntity, nothing special other than red
class EnemyEntity(Entity):
    def __init__(self, world, position=Vector2(0, 0), maximum_speed=100, drag=0.85):
        super(EnemyEntity, self).__init__(world, position, maximum_speed, drag, 3000)
        self.color = (255, 0, 0)


# arrow entity - not really an "entity", but a semi-hack to introduce physics based arrows
class ArrowEntity(Entity):
    def __init__(self, world, position, maximum_speed, direction, damage, source, pierce_count):
        super(ArrowEntity, self).__init__(world, position, maximum_speed, 1)
        self.damage = damage
        self.source = source
        self.acceleration = direction * self.maximum_speed
        self.already_hit = list()
        if isinstance(source, Player):
            self.color = (255, 255, 255)
        else:
            self.color = (0, 0, 0)
        self.pierce_count = pierce_count

    def deal_damage(self, target: Entity):
        if isinstance(self.source, Player):
            self.source.score += self.damage
        target.health -= self.damage

    # tick the arrow for movement
    def tick_entity(self, dt):
        colliding = self.get_colliding_entities()
        # check if we hit something
        if colliding and colliding[0] is not self.source and colliding[0] not in self.already_hit:
            # we did! deal damage and don't hit again
            self.deal_damage(colliding[0])
            self.already_hit.append(colliding[0])
            # check if we can pierce; if we can, don't die.
            if self.pierce_count > 0:
                self.pierce_count -= 1
            else:
                self.health = 0
        # die if it's outside
        if self.position not in self.world:
            self.health = 0
        super(ArrowEntity, self).tick_entity(dt)

    # gets any colliding enemies
    def get_colliding_entities(self):
        box = Rectangle(Vector2(self.position.x - (self.size.x / 2), self.position.y - (self.size.y / 2)),
                        Vector2(self.position.x + (self.size.x / 2), self.position.y + (self.size.y / 2)))
        entities = list()
        for entity in self.world.entities:
            if entity is not self and not isinstance(entity, ArrowEntity) and entity.position in box:
                entities.append(entity)
        return entities


# represents a player entity
class Player(Entity):
    def __init__(self, world, position=Vector2(0, 0), maximum_speed=100, drag=0.85):
        super(Player, self).__init__(world, position, maximum_speed, drag)
        self.color = (0, 255, 0)
        self.skill = None
        self.god_mode = False
        self.score = 0

    # make sure we tick godmode
    def tick_entity(self, dt):
        if self.god_mode:
            self.health = self.maximum_health
        # add passive regen
        self.health = min(self.health + 5, self.maximum_health)
        super(Player, self).tick_entity(dt)
