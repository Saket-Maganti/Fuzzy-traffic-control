import pygame
from src.Common import Lane, TrafficStatus
from src.Config import Config


class Vehicle:
    """
    Represents a vehicle in a traffic lane.
    Handles drawing, movement, and interactions with traffic lights.
    """

    def __init__(self, x, y, lane: Lane, image, surface, traffic_light):
        if lane != traffic_light.lane:
            raise Exception('Vehicle and Traffic Light must belong to the same lane.')

        self.x = x
        self.y = y
        self.lane = lane
        self.surface = surface
        self.traffic_light = traffic_light

        # Scale vehicle image according to direction
        if lane in [Lane.left_to_right, Lane.right_to_left]:
            size = (Config['vehicle']['body_length'], Config['vehicle']['body_width'])
        else:
            size = (Config['vehicle']['body_width'], Config['vehicle']['body_length'])

        self.image = pygame.transform.scale(image, size)

    @property
    def width(self):
        return self.image.get_width()

    @property
    def height(self):
        return self.image.get_height()

    @property
    def center_x(self):
        return self.x + self.width / 2

    @property
    def center_y(self):
        return self.y + self.height / 2

    def draw(self):
        """Render vehicle onto the surface."""
        self.surface.blit(self.image, (self.x, self.y))

    def move(self, front_vehicle=None):
        """Handles vehicle motion and safe stopping."""
        speed = Config['vehicle']['speed']
        safe_distance = Config['vehicle']['safe_distance']
        stopping_due_to_signal = self.traffic_light.status != TrafficStatus.green and self.is_behind_traffic_light()

        if self.lane == Lane.left_to_right:
            self.x += speed
            if front_vehicle:
                self.x = min(self.x, front_vehicle.x - safe_distance - self.width)
            if stopping_due_to_signal:
                self.x = min(self.x, self.traffic_light.x - self.traffic_light.width / 2 - self.width)

        elif self.lane == Lane.right_to_left:
            self.x -= speed
            if front_vehicle:
                self.x = max(self.x, front_vehicle.x + front_vehicle.width + safe_distance)
            if stopping_due_to_signal:
                self.x = max(self.x, self.traffic_light.x + self.traffic_light.width * 1.5)

        elif self.lane == Lane.top_to_bottom:
            self.y += speed
            if front_vehicle:
                self.y = min(self.y, front_vehicle.y - safe_distance - self.height)
            if stopping_due_to_signal:
                self.y = min(self.y, self.traffic_light.y - self.traffic_light.height / 2 - self.height)

        elif self.lane == Lane.bottom_to_top:
            self.y -= speed
            if front_vehicle:
                self.y = max(self.y, front_vehicle.y + front_vehicle.height + safe_distance)
            if stopping_due_to_signal:
                self.y = max(self.y, self.traffic_light.y + self.traffic_light.height)

    def is_behind_traffic_light(self):
        """Returns True if the vehicle is behind the traffic light (used for stopping logic)."""
        if self.lane == Lane.left_to_right:
            return self.x + self.width <= self.traffic_light.x + self.traffic_light.width
        elif self.lane == Lane.right_to_left:
            return self.traffic_light.x + self.traffic_light.width <= self.x
        elif self.lane == Lane.top_to_bottom:
            return self.y + self.height <= self.traffic_light.y
        elif self.lane == Lane.bottom_to_top:
            return self.traffic_light.y + self.traffic_light.height <= self.y
        return False

    def inside_canvas(self) -> bool:
        """Checks if the vehicle is still within the screen boundaries."""
        return (
            0 <= self.x <= Config['simulator']['screen_width'] - self.width and
            0 <= self.y <= Config['simulator']['screen_height'] - self.height
        )
