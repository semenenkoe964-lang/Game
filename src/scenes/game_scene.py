import pygame

from src.algorithms.bsp_generator import BSPGenerator
from src.controllers.input_handler import InputHandler
from src.core.settings import (
    CHEST_INTERACTION_RADIUS,
    EXIT_INTERACTION_RADIUS,
    FLOOR_CONFIGS,
    KEY_INTERACTION_RADIUS,
    MAX_FLOORS,
)
from src.models.mummy import FastMummy, NormalMummy
from src.models.player import Player
from src.scenes.death_scene import DeathScene
from src.scenes.pause_scene import PauseScene
from src.scenes.win_scene import WinScene
from src.systems.collision_system import circle_overlap
from src.systems.combat_system import CombatSystem
from src.systems.enemy_ai_system import EnemyAISystem
from src.systems.lighting_system import LightingSystem
from src.systems.loot_system import LootSystem
from src.systems.movement_system import MovementSystem
from src.views.ascii_renderer import ASCIIRenderer
from src.views.camera import Camera
from src.views.ui_renderer import UIRenderer


class GameScene:
    def __init__(self, scene_manager, floor_number: int, player: Player | None = None):
        pygame.mouse.set_visible(False)
        self.scene_manager = scene_manager
        self.floor_number = floor_number
        self.camera = Camera()
        self.ascii_renderer = ASCIIRenderer()
        self.ui_renderer = UIRenderer()
        self.lighting_system = LightingSystem()
        self.combat_system = CombatSystem()
        self.enemy_ai_system = EnemyAISystem()
        self.bullets = []
        self.message = ""
        self.message_timer = 0.0
        self.aim_screen_position = pygame.Vector2(pygame.mouse.get_pos())
        self.aim_world_position = pygame.Vector2(0, 0)
        self.is_shooting = False

        self.floor_map = BSPGenerator().generate_valid_floor(FLOOR_CONFIGS[floor_number])
        start_position = self.floor_map.tile_to_world(self.floor_map.start_tile)
        self.player = player or Player(start_position)
        self.player.set_position(start_position)
        self.player.has_key = False

        self.chests = LootSystem.create_chests_for_floor(self.floor_map)
        self.mummies = self._create_mummies()
        self.camera.follow(self.player.position, self.floor_map)
        self._update_aim_cursor()

    def _create_mummies(self) -> list:
        mummies = []
        for enemy_type, tile in self.floor_map.enemy_spawns:
            position = self.floor_map.tile_to_world(tile)
            if enemy_type == "fast":
                mummies.append(FastMummy(position))
            else:
                mummies.append(NormalMummy(position))
        return mummies

    def handle_events(self, events) -> None:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.is_shooting = True
                continue
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.is_shooting = False
                continue
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                self.scene_manager.set_scene(PauseScene(self.scene_manager, self))
            elif event.key == pygame.K_q:
                self.player.switch_weapon()
            elif event.key == pygame.K_e:
                self._interact()

    def update(self, dt: float) -> None:
        self._update_message(dt)
        self.player.update_weapons(dt)

        movement = InputHandler.movement_vector()
        if movement.length_squared():
            self.player.last_direction = movement.normalize()
        old_player_position = self.player.position.copy()
        MovementSystem.move_with_collisions(self.player, movement, dt, self.floor_map)
        self.player.update_animation(dt, self.player.position - old_player_position)
        self.camera.follow(self.player.position, self.floor_map)
        self._update_aim_cursor()

        if self.is_shooting:
            self._shoot_at_cursor()

        self.bullets = self.combat_system.update_bullets(
            self.bullets,
            self.mummies,
            self.floor_map,
            self.player,
            dt,
        )
        self.mummies = [mummy for mummy in self.mummies if mummy.alive]
        self.enemy_ai_system.update(self.mummies, self.player, self.floor_map, dt)
        self.camera.follow(self.player.position, self.floor_map)

        if self.player.health <= 0:
            self.scene_manager.set_scene(DeathScene(self.scene_manager, self.player.score))

    def _interact(self) -> None:
        if not self.player.has_key and self.floor_map.key_tile is not None:
            key_position = self.floor_map.tile_to_world(self.floor_map.key_tile)
            if circle_overlap(self.player.position, KEY_INTERACTION_RADIUS, key_position, 10):
                self.player.has_key = True
                self._show_message("Found the key")
                return

        for chest in self.chests:
            if chest.opened:
                continue
            if circle_overlap(self.player.position, CHEST_INTERACTION_RADIUS, chest.position, chest.radius):
                message = LootSystem.apply_loot(self.player, chest.open())
                self._show_message(message)
                return

        if self.floor_map.exit_tile is None:
            return
        exit_position = self.floor_map.tile_to_world(self.floor_map.exit_tile)
        if not circle_overlap(self.player.position, EXIT_INTERACTION_RADIUS, exit_position, 12):
            return

        if not self.player.has_key:
            self._show_message("The exit is locked")
            return

        if self.floor_number >= MAX_FLOORS:
            self.scene_manager.set_scene(WinScene(self.scene_manager, self.player.score))
        else:
            self.scene_manager.set_scene(
                GameScene(self.scene_manager, self.floor_number + 1, player=self.player)
            )

    def _update_aim_cursor(self) -> None:
        self.aim_screen_position = pygame.Vector2(pygame.mouse.get_pos())
        self.aim_world_position = pygame.Vector2(self.camera.screen_to_world(self.aim_screen_position))

    def _aim_direction(self) -> pygame.Vector2:
        direction = self.aim_world_position - self.player.position
        if direction.length_squared() == 0:
            return pygame.Vector2(1, 0)
        return direction.normalize()

    def _shoot_at_cursor(self) -> None:
        aim_direction = self._aim_direction()
        self.player.last_direction = aim_direction
        self.bullets.extend(self.combat_system.fire_player_weapon(self.player, aim_direction))

    def _show_message(self, message: str) -> None:
        self.message = message
        self.message_timer = 2.0

    def _update_message(self, dt: float) -> None:
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

    def draw(self, screen) -> None:
        self.ascii_renderer.draw_world(
            screen,
            self.floor_map,
            self.camera,
            self.lighting_system,
            self.player,
            self.chests,
            self.mummies,
            self.bullets,
        )
        self.lighting_system.draw_overlay(screen, self.camera, self.player, self.floor_map)
        self.ui_renderer.draw_game_ui(
            screen,
            self.player,
            self.floor_number,
            MAX_FLOORS,
            self.message,
        )
        self.ui_renderer.draw_crosshair(screen, self.aim_screen_position)
