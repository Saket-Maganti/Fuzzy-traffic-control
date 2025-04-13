import os
import pygame

from src.Common import TrafficStatus, DoubleLane, Lane
from src.Config import Config
from src.Entity.TrafficLight import TrafficLight
from src.Fuzzy import Fuzzy


class TrafficController:
    def __init__(self, surface):
        self.surface = surface
        self.fuzzy = Fuzzy()
        self.latest_green_light_extension = 0

        # Load dimensions and config values
        cfg = Config['traffic_light']
        self.screen_width = Config['simulator']['screen_width']
        self.screen_height = Config['simulator']['screen_height']
        self.body_height = cfg['body_height']
        self.body_width = cfg['body_width']
        self.offset = cfg['distance_from_center']

        self.traffic_lights = {}

        # Initialize traffic lights
        self._init_lights()

    def _init_lights(self):
        coords = {
            Lane.left_to_right: (
                self.screen_width / 2 - self.offset[0] - self.body_width,
                self.screen_height / 2 - self.offset[1] - self.body_height
            ),
            Lane.right_to_left: (
                self.screen_width / 2 + self.offset[0],
                self.screen_height / 2 + self.offset[1]
            ),
            Lane.top_to_bottom: (
                self.screen_height / 2 + self.offset[1],
                self.screen_width / 2 - self.offset[0] - self.body_width
            ),
            Lane.bottom_to_top: (
                self.screen_height / 2 - self.offset[1] - self.body_height,
                self.screen_width / 2 + self.offset[0]
            )
        }

        for lane, (x, y) in coords.items():
            self.create_traffic_light(x, y, lane)

    def create_traffic_light(self, x, y, lane: Lane):
        """Creates and configures a traffic light for a given lane."""
        images_dir = os.path.join(os.getcwd(), 'images', 'traffic_light')
        rotation_map = {
            Lane.bottom_to_top: 90,
            Lane.right_to_left: 180,
            Lane.top_to_bottom: 270,
        }

        rotation = rotation_map.get(lane, 0)
        images = {
            TrafficStatus.red: self._design_light_image(images_dir, 'traffic_light_red.png', rotation),
            TrafficStatus.green: self._design_light_image(images_dir, 'traffic_light_green.png', rotation),
            TrafficStatus.yellow: self._design_light_image(images_dir, 'traffic_light_yellow.png', rotation)
        }

        light = TrafficLight(x, y, lane, images, self.surface)
        if lane in [Lane.top_to_bottom, Lane.bottom_to_top]:
            light.change_status(TrafficStatus.red)
        self.traffic_lights[lane] = light

    def _design_light_image(self, base_path, filename, rotation):
        """Load and rotate traffic light image."""
        img = pygame.image.load(os.path.join(base_path, filename))
        img = pygame.transform.scale(img, (self.body_width, self.body_height))
        return pygame.transform.rotate(img, rotation)

    def get_traffic_lights(self, double_lane: DoubleLane):
        """Returns the pair of traffic lights for a double lane."""
        if double_lane == DoubleLane.Horizontal:
            return [self.traffic_lights[Lane.left_to_right], self.traffic_lights[Lane.right_to_left]]
        elif double_lane == DoubleLane.Vertical:
            return [self.traffic_lights[Lane.top_to_bottom], self.traffic_lights[Lane.bottom_to_top]]
        return []

    def update_and_draw_traffic_lights(self):
        """Auto-updates each traffic light and draws them on screen."""
        for lane, light in self.traffic_lights.items():
            opposite_status = self.get_opposite_status(lane)
            light.auto_update(opposite_status)
            light.draw()
            light.draw_countdown()

    def get_opposite_status(self, lane: Lane):
        """Determine the status of the perpendicular lane."""
        if lane in [Lane.left_to_right, Lane.right_to_left]:
            return self.traffic_lights[Lane.bottom_to_top].status
        return self.traffic_lights[Lane.left_to_right].status

    def get_current_active_lane(self) -> DoubleLane:
        """Get which double lane currently has green light."""
        if self.traffic_lights[Lane.left_to_right].status == TrafficStatus.green:
            return DoubleLane.Horizontal
        elif self.traffic_lights[Lane.top_to_bottom].status == TrafficStatus.green:
            return DoubleLane.Vertical
        return None

    def calculate_fuzzy_score(self, arriving_green_light_car, behind_red_light_car, extension_count):
        """Delegates fuzzy calculation to the fuzzy engine."""
        return self.fuzzy.get_extension(arriving_green_light_car, behind_red_light_car, extension_count)

    def get_green_light_extension(self):
        """Get the current green light extension."""
        current = self.get_current_active_lane()
        if not current:
            return self.latest_green_light_extension

        if current == DoubleLane.Vertical:
            self.latest_green_light_extension = self.traffic_lights[Lane.bottom_to_top].duration_extension[TrafficStatus.green]
        elif current == DoubleLane.Horizontal:
            self.latest_green_light_extension = self.traffic_lights[Lane.left_to_right].duration_extension[TrafficStatus.green]

        return self.latest_green_light_extension

    def set_green_light_extension(self, extension):
        """Apply green light extension to current lane."""
        current = self.get_current_active_lane()
        if current:
            for light in self.get_traffic_lights(current):
                light.set_green_light_extension(extension)

    def clear_all_green_light_extension(self):
        """Reset all green light extensions to zero."""
        for light in self.traffic_lights.values():
            light.set_green_light_extension(0)

    def get_green_light_remaining(self):
        """Return remaining green light time."""
        current = self.get_current_active_lane()
        if current == DoubleLane.Vertical:
            return self.traffic_lights[Lane.bottom_to_top].get_green_light_remaining_time()
        elif current == DoubleLane.Horizontal:
            return self.traffic_lights[Lane.left_to_right].get_green_light_remaining_time()
        return 0

    def in_transition(self) -> bool:
        """True if currently transitioning between lanes."""
        return self.get_current_active_lane() is None
