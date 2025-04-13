import glob
import pygame
import random
import numpy as np

from src.Common import Lane
from src.Config import Config
from src.Entity.Vehicle import Vehicle
from src.Entity.TrafficLight import TrafficLight


class VehicleController:
    def __init__(self, surface):
        self.surface = surface
        self.counter = 0

        self.screen_height = Config['simulator']['screen_height']
        self.screen_width = Config['simulator']['screen_width']
        self.vehicle_width = Config['vehicle']['body_width']
        self.vehicle_length = Config['vehicle']['body_length']
        self.bumper_distance = Config['simulator']['bumper_distance']
        self.safe_distance = Config['vehicle']['safe_distance']
        self.safe_spawn_factor = Config['vehicle']['safe_spawn_factor']
        self.frame_rate = Config['simulator']['frame_rate']
        self.moving_window = Config['simulator']['moving_averages_period']

        self.vehicles = {lane: [] for lane in Lane}
        self.num_vehicles_behind_traffic = {lane: [] for lane in Lane}
        self.vehicle_images = self._load_vehicle_images()

    def _load_vehicle_images(self):
        """Load vehicle images from folders per lane direction."""
        image_map = {}
        for lane in Lane:
            dir_name = f'images/vehicles_{lane.name}/*.png'
            image_map[lane] = [pygame.image.load(f) for f in glob.glob(dir_name)]
        return image_map

    def _random_image(self, lane: Lane):
        return random.choice(self.vehicle_images[lane]) if self.vehicle_images[lane] else None

    def _last_vehicle(self, lane: Lane):
        return self.vehicles[lane][-1] if self.vehicles[lane] else None

    def get_vehicles(self, lane: Lane):
        return self.vehicles[lane]

    def create_vehicle(self, lane: Lane, traffic_light: TrafficLight):
        """Creates a new vehicle if spacing allows it."""
        if lane != traffic_light.lane:
            raise ValueError("Vehicle and traffic light must be in the same lane")

        img = self._random_image(lane)
        if img is None:
            return  # Skip if no image loaded

        last = self._last_vehicle(lane)
        x, y = 0, 0
        too_close = False

        if lane == Lane.left_to_right:
            x = 0
            y = self.screen_height / 2 - self.vehicle_width - self.bumper_distance
            if last and last.x - self.safe_distance * self.safe_spawn_factor < x + self.vehicle_length:
                too_close = True

        elif lane == Lane.right_to_left:
            x = self.screen_width - self.vehicle_length
            y = self.screen_height / 2 + self.bumper_distance
            if last and last.x + self.vehicle_length + self.safe_distance * self.safe_spawn_factor > x:
                too_close = True

        elif lane == Lane.top_to_bottom:
            x = self.screen_width / 2 + self.bumper_distance
            y = 0
            if last and last.y - self.safe_distance * self.safe_spawn_factor < y + self.vehicle_length:
                too_close = True

        elif lane == Lane.bottom_to_top:
            x = self.screen_width / 2 - self.vehicle_width - self.bumper_distance
            y = self.screen_height - self.vehicle_length
            if last and last.y + self.vehicle_length + self.safe_distance * self.safe_spawn_factor > y:
                too_close = True

        if too_close:
            return

        vehicle = Vehicle(x, y, lane, img, self.surface, traffic_light)
        self.vehicles[lane].append(vehicle)
        self.counter += 1

    def update_and_draw_vehicles(self):
        """Move and draw vehicles for all lanes."""
        for lane, vehicles in self.vehicles.items():
            for i, vehicle in enumerate(vehicles):
                front = vehicles[i - 1] if i > 0 else None
                vehicle.move(front)
                vehicle.draw()

    def destroy_vehicles_outside_canvas(self):
        """Remove vehicles that are no longer on screen."""
        for lane in Lane:
            self.vehicles[lane] = [v for v in self.vehicles[lane] if v.inside_canvas()]

    def update_num_vehicles_behind_traffic(self):
        """Track number of vehicles behind red lights and maintain moving average."""
        max_len = self.frame_rate * self.moving_window
        for lane in Lane:
            count = sum(1 for v in self.vehicles[lane] if v.is_behind_traffic_light())
            self.num_vehicles_behind_traffic[lane].append(count)
            if len(self.num_vehicles_behind_traffic[lane]) > max_len:
                self.num_vehicles_behind_traffic[lane].pop(0)

    def get_moving_averages_num_vehicles_behind_traffic(self):
        """Return moving average per lane for vehicles behind traffic."""
        return {
            lane: np.mean(self.num_vehicles_behind_traffic[lane]) if self.num_vehicles_behind_traffic[lane] else 0
            for lane in Lane
        }
