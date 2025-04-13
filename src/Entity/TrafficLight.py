import time
import pygame

from src.Common import TrafficStatus, Lane
from src.Config import Config


class TrafficLight:
    """
    Represents a single traffic light with fuzzy extension support.
    Manages light status, timing, and drawing to the simulation surface.
    """

    def __init__(self, x, y, lane, images, surface, status=TrafficStatus.green):
        self.x = x
        self.y = y
        self.lane = lane
        self.surface = surface
        self.images = images  # {TrafficStatus: pygame.Surface}

        self.duration = {
            TrafficStatus.green: Config['traffic_light']['green_light_duration'],
            TrafficStatus.yellow: Config['traffic_light']['yellow_light_duration'],
            TrafficStatus.red: Config['traffic_light']['red_light_duration']
        }

        self.duration_extension = {
            TrafficStatus.green: 0,
            TrafficStatus.yellow: 0,
            TrafficStatus.red: 0
        }

        current_time = time.time()
        self.start_time = {
            TrafficStatus.green: current_time,
            TrafficStatus.yellow: current_time,
            TrafficStatus.red: current_time
        }

        self.status = status

    @property
    def width(self):
        return Config['traffic_light']['body_width']

    @property
    def height(self):
        return Config['traffic_light']['body_height']

    @property
    def center_x(self):
        return self.x + self.width / 2

    @property
    def center_y(self):
        return self.y + self.height / 2

    def draw(self):
        """Render the traffic light image based on current status."""
        self.surface.blit(self.images[self.status], (self.x, self.y))

    def change_status(self, status: TrafficStatus):
        """Manually change the traffic light status."""
        self.status = status
        self.start_time[status] = time.time()

    def auto_update(self, opposite_status: TrafficStatus):
        """
        Automatically transitions traffic light state after the duration.
        Prevents green-to-green clashes with the opposite light.
        """
        elapsed = time.time() - self.start_time[self.status]
        total_duration = self.duration[self.status] + self.duration_extension[self.status]
        remaining = total_duration - elapsed

        if remaining > 0:
            return

        if self.status == TrafficStatus.green:
            self.status = TrafficStatus.yellow
        elif self.status == TrafficStatus.yellow:
            self.status = TrafficStatus.red
        elif self.status == TrafficStatus.red:
            if opposite_status == TrafficStatus.green:
                return
            if abs(remaining) < Config['simulator']['gap_between_traffic_switch']:
                return
            self.status = TrafficStatus.green

        self.start_time[self.status] = time.time()
        return self.status

    def draw_countdown(self):
        """Draw countdown timer near the traffic light."""
        remaining = self.get_green_light_remaining_time()
        color = {
            TrafficStatus.green: Config['colors']['traffic_green'],
            TrafficStatus.yellow: Config['colors']['traffic_yellow'],
            TrafficStatus.red: Config['colors']['traffic_red']
        }.get(self.status, Config['colors']['black'])

        font = pygame.font.SysFont('Comic Sans MS', 12, True)
        text = font.render(f"{round(max(0, remaining), 1)}", True, color)

        # Position label based on lane orientation
        pos_x, pos_y = self.x, self.y
        if self.lane == Lane.left_to_right:
            pos_y -= self.height
        elif self.lane == Lane.right_to_left:
            pos_y += self.height * 1.25
        elif self.lane == Lane.top_to_bottom:
            pos_x += self.width * 2
        elif self.lane == Lane.bottom_to_top:
            pos_x -= self.width * 2

        self.surface.blit(text, (pos_x, pos_y))

    def set_green_light_extension(self, extension):
        """Set the fuzzy logic green light extension."""
        self.duration_extension[TrafficStatus.green] = extension

    def get_green_light_remaining_time(self):
        """Returns the remaining time for the current light phase."""
        elapsed = time.time() - self.start_time[self.status]
        return max(0.0, self.duration[self.status] + self.duration_extension[self.status] - elapsed)
