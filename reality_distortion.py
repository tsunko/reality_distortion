from world.worldgen import WorldGenerator
from vector import Vector2
from ui.camera import Camera
from pathfinding import a_star_pathfind
from skill.support import *
from pyglet.gl import *
from entity import EnemyEntity, Player
import pyglet
from ui import rendering
from skill.skill import BowAttack
from concurrent.futures import ThreadPoolExecutor
import logging
import random
from goal import *
from pyglet.window import FPSDisplay
from pyglet.text import Label


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

HALF_SCREEN_WIDTH = SCREEN_WIDTH // 2
HALF_SCREEN_HEIGHT = SCREEN_HEIGHT // 2


if __name__ == "__main__":
    logging.basicConfig(format="[%(levelname)s @ %(name)s.%(funcName)s:%(lineno)s] %(message)s")
    window = pyglet.window.Window(SCREEN_WIDTH, SCREEN_HEIGHT)

    # create thread pool to allow async pathfinding
    pool = ThreadPoolExecutor(max_workers=2)
    generator = WorldGenerator(15, Vector2(100, 100), Vector2(300, 300), 50)
    # generate default world and dummy enemy
    world = generator.generate()
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, 2)
    world.entities.append(EnemyEntity(world, Vector2(25, 25)))
    # enable player and give it the default Arrow Attack
    player = Player(world)
    player.skill = BowAttack()
    # add player, initialize labels
    world.entities.append(player)
    fps_display = FPSDisplay(window)
    fps_display.label.x += 200
    support_display = Label("No Active Supports", font_size=12,
                            x=window.width//2, y=12, anchor_x="center", anchor_y="center")
    score_display = Label("Score: ", font_size=12, x=window.width//2, y=24, anchor_x="center", anchor_y="center")

    @window.event
    def on_draw():
        window.clear()

        # translate to isometric view
        camera.initialize_ortho()
        camera.translate_with_position()

        # draw world and entities
        rendering.draw_world(world)
        rendering.draw_entities(world.entities)

        # reset ortho and draw UI now
        camera.reset_identity()
        rendering.draw_ui(SCREEN_WIDTH, SCREEN_HEIGHT, world, player)

        # draw labels on screen
        fps_display.draw()
        support_display.draw()
        score_display.draw()


    @window.event
    def on_mouse_motion(x, y, dx, dy):
        # find zone where cursor is in
        zone = world.get_zone_containing_point(screen_to_game(x, y).to_2d())
        if zone is None:
            return
        for other_zone in world.zones:
            # brighten up zone and make it known to the user that this is the selected
            if other_zone is zone:
                color = (128, 128, 128)
            # elif other_zone in zone.get_neighbors():
            #     color = (64, 64, 64)
            else:
                color = (16, 16, 16)
            other_zone.color = color

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        # find where the user clicked in game world
        game_coord = screen_to_game(x, y).to_2d()
        if button == pyglet.window.mouse.RIGHT:
            # check if player is alive
            if player.health > 0:
                # point = screen_to_game(x, y).to_2d()
                # paths[:] = []
                # for entity in world.entities:
                #     if entity is not player:
                #         entity.follow_path(a_star_pathfind(world, entity.position, point))
                # cast skill
                player.skill.use(world, player, (game_coord - player.position).normalize())
        elif button == pyglet.window.mouse.LEFT:
            # check if player is alive
            if player.health > 0:
                # try a star pathfinding to move player
                if player.planning is not None:
                    player.planning.cancel()
                    player.planning = None
                player.planning = pool.submit(a_star_pathfind, world, player.position, game_coord)\
                    .add_done_callback(lambda future: player.follow_path(future.result()))

    @window.event
    def on_mouse_drag(x, y, dx, dy, button, modifiers):
        # camera.position -= Vector2(dx, dy)
        pass

    @window.event
    def on_key_press(symbol, modifiers):
        # check if player wants to regenerate the world
        if symbol == pyglet.window.key.R:
            if player.god_mode:
                return
            global world
            world = WorldGenerator(15, Vector2(100, 100), Vector2(300, 300), 50).generate()
            # reset camera and player stats
            camera.position = Vector2(0, 0)
            player.velocity = Vector2(0, 0)
            player.acceleration = Vector2(0, 0)
            player.position = Vector2(0, 0)
            player.goals = dict()
            player.health = player.maximum_health
            # cancel any active pathfinding
            if player.planning is not None:
                player.planning.cancel()
                player.planning = None
            player.skill = BowAttack()
            player.active_supports = []
            player.god_mode = True
            player.score = 0
            # give player godmode, but disable after 3 seconds
            pyglet.clock.schedule_once(disable_god_mode, 3.0)
            world.entities.append(player)
            # spawn enemies now and update support display
            spawn_enemies()
            update_support_display()
        elif symbol == pyglet.window.key._1:
            # add multi proj
            player.toggle_support(MultipleProjectilesSupport())
            update_support_display()
        elif symbol == pyglet.window.key._2:
            # add slower proj
            player.toggle_support(SlowerProjectileSupport())
            update_support_display()
        elif symbol == pyglet.window.key._3:
            # add heavy draw
            player.toggle_support(HeavyDrawSupport())
            update_support_display()
        # elif symbol == pyglet.window.key._3:
        #     player.toggle_support(ChainSupport())

    def disable_god_mode(dt):
        # callback for 3 seconds after to disable godmode
        player.god_mode = False

    def update_support_display():
        # generates a string based on current supports
        if not player.active_supports:
            support_display.text = "No Active Supports"
        else:
            support_display.text = "Active Support: "
            for support in player.active_supports:
                support_display.text += support.__str__() + ", "
            support_display.text = support_display.text[:-2]

    def spawn_enemies(count=25):
        for i in range(count):
            # give them a random zone to spawn in
            random_zone = random.choice(world.zones)
            # give them a position inside of the random zone
            spawning_location = Vector2(
                random.randint(random_zone.bottom_left.x, random_zone.top_right.x),
                random.randint(random_zone.bottom_left.y, random_zone.top_right.y),
            )
            # create enemy and add their goal (shoot at player)
            other_entity = EnemyEntity(world, spawning_location)
            other_entity.add_goal(ShootAtPlayerGoal(other_entity, player))
            # spawn in world
            world.entities.append(other_entity)

    def screen_to_game(x, y):
        # general formula to convert screen coords to in-game isometric coords
        return Vector2((x - HALF_SCREEN_WIDTH + camera.position.x) / camera.zoom,
                       (y - HALF_SCREEN_HEIGHT + camera.position.y) / camera.zoom)

    def tick(dt):
        # camera follows player
        camera_pos = player.position.to_iso()
        camera.position.x = camera_pos.x * camera.zoom
        camera.position.y = camera_pos.y * camera.zoom
        # tick world and show score
        world.tick_world(dt)
        score_display.text = "Score: " + str(player.score)

    pyglet.clock.schedule_interval(tick, 1 / 60)
    pyglet.app.run()
