import pygame
import time

from src.Common import Lane, DoubleLane
from src.Config import Config
from src.Controller.VehicleController import VehicleController
from src.Controller.TrafficController import TrafficController
from src.Controller.BackgroundController import BackgroundController


class Simulator:
    def __init__(self, caption):
        self.caption = caption
        self.surface = pygame.display.set_mode((
            Config['simulator']['screen_width'],
            Config['simulator']['screen_height']
        ))

        # Core controllers
        self.vehicle_ctrl = VehicleController(self.surface)
        self.traffic_ctrl = TrafficController(self.surface)
        self.background_ctrl = BackgroundController(
            self.surface,
            self.traffic_ctrl.get_traffic_lights(DoubleLane.Horizontal) +
            self.traffic_ctrl.get_traffic_lights(DoubleLane.Vertical)
        )

        self.clock = pygame.time.Clock()
        self.start_time = time.time()
        self.extension_notification_start_time = time.time() - 10

        # Traffic flow and spawn rate control
        self.green_light_remaining_time = Config['traffic_light']['green_light_duration']
        self.moving_averages = self.vehicle_ctrl.get_moving_averages_num_vehicles_behind_traffic()
        self.is_extended = False
        self.horizontal = 0
        self.vertical = 0

        self.HORIZONTAL_SPAWN_EVENT = pygame.USEREVENT + 1
        self.VERTICAL_SPAWN_EVENT = pygame.USEREVENT + 2

    def start(self):
        """Start the simulator loop."""
        pygame.init()
        pygame.display.set_caption(self.caption)
        self.initialize()
        self.main_loop()
        pygame.quit()
        quit()

    def initialize(self):
        """Initial setup before main loop starts."""
        self.spawn(DoubleLane.Horizontal)
        self.spawn(DoubleLane.Vertical)

    def spawn(self, double_lane: DoubleLane):
        """Spawn two vehicles in opposing lanes."""
        if double_lane == DoubleLane.Horizontal:
            self.spawn_single_vehicle(Lane.left_to_right)
            self.spawn_single_vehicle(Lane.right_to_left)
        elif double_lane == DoubleLane.Vertical:
            self.spawn_single_vehicle(Lane.bottom_to_top)
            self.spawn_single_vehicle(Lane.top_to_bottom)

    def spawn_single_vehicle(self, lane: Lane):
        """Spawn a single vehicle for a specific lane."""
        self.vehicle_ctrl.create_vehicle(lane, self.traffic_ctrl.traffic_lights[lane])

    def calculate_fuzzy_score(self, moving_averages):
        """Call fuzzy controller and return crisp extension."""
        lane = self.traffic_ctrl.get_current_active_lane()
        ext_count = 1 if self.is_extended else 0

        if lane == DoubleLane.Vertical:
            return self.traffic_ctrl.calculate_fuzzy_score(
                moving_averages[Lane.top_to_bottom],
                moving_averages[Lane.left_to_right],
                ext_count
            )
        elif lane == DoubleLane.Horizontal:
            return self.traffic_ctrl.calculate_fuzzy_score(
                moving_averages[Lane.left_to_right],
                moving_averages[Lane.top_to_bottom],
                ext_count
            )

    def handle_events(self):
        """React to user or system-generated events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True  # signal to exit

            if event.type == self.HORIZONTAL_SPAWN_EVENT:
                rate = self.background_ctrl.get_spawn_rate(DoubleLane.Horizontal)
                pygame.time.set_timer(self.HORIZONTAL_SPAWN_EVENT, Config['simulator']['spawn_rate'][rate])
                self.spawn(DoubleLane.Horizontal)

            if event.type == self.VERTICAL_SPAWN_EVENT:
                rate = self.background_ctrl.get_spawn_rate(DoubleLane.Vertical)
                pygame.time.set_timer(self.VERTICAL_SPAWN_EVENT, Config['simulator']['spawn_rate'][rate])
                self.spawn(DoubleLane.Vertical)

            if event.type == pygame.MOUSEBUTTONDOWN:
                for dl in [DoubleLane.Horizontal, DoubleLane.Vertical]:
                    for rate in ['slow', 'medium', 'fast']:
                        if self.background_ctrl.spawn_rate_buttons[dl][rate].collidepoint(event.pos):
                            self.background_ctrl.set_spawn_rate(dl, rate)

        return False

    def main_loop(self):
        """Main simulation loop."""
        game_over = False

        pygame.time.set_timer(self.HORIZONTAL_SPAWN_EVENT, Config['simulator']['spawn_rate']['slow'])
        pygame.time.set_timer(self.VERTICAL_SPAWN_EVENT, Config['simulator']['spawn_rate']['slow'])

        while not game_over:
            game_over = self.handle_events()

            self.update_controllers()
            self.draw_ui()

            pygame.display.update()
            self.clock.tick(Config['simulator']['frame_rate'])

    def update_controllers(self):
        """Update state of simulation components."""
        self.traffic_ctrl.update_and_draw_traffic_lights()
        self.vehicle_ctrl.destroy_vehicles_outside_canvas()
        self.vehicle_ctrl.update_and_draw_vehicles()
        self.vehicle_ctrl.update_num_vehicles_behind_traffic()

        # Update moving average every second
        if round((time.time() - self.start_time), 1) % Config['simulator']['static_duration'] == 0:
            self.moving_averages = self.vehicle_ctrl.get_moving_averages_num_vehicles_behind_traffic()

        # Check for fuzzy green light extension
        current_green_time = self.traffic_ctrl.get_green_light_remaining()
        direction_changed = current_green_time > self.green_light_remaining_time
        self.green_light_remaining_time = current_green_time

        if not self.is_extended:
            if current_green_time <= Config['simulator']['seconds_before_extension']:
                fuzzy_score = self.calculate_fuzzy_score(self.moving_averages)
                self.horizontal = self.moving_averages[Lane.left_to_right]
                self.vertical = self.moving_averages[Lane.top_to_bottom]
                self.traffic_ctrl.set_green_light_extension(fuzzy_score)
                self.extension_notification_start_time = time.time()
                self.is_extended = True
        elif direction_changed:
            self.traffic_ctrl.clear_all_green_light_extension()
            self.is_extended = False

    def draw_ui(self):
        """Render UI components and visual indicators."""
        self.background_ctrl.refresh_screen()
        self.background_ctrl.draw_road_markings()
        self.background_ctrl.draw_vehicle_count(self.vehicle_ctrl.counter)
        self.background_ctrl.draw_spawn_rate_buttons()
        self.background_ctrl.draw_light_durations(self.traffic_ctrl.get_green_light_extension())
        self.background_ctrl.draw_moving_averages(self.moving_averages)

        if time.time() - self.extension_notification_start_time < Config['simulator']['fuzzy_notification_duration']:
            self.background_ctrl.draw_extension_notification(
                self.traffic_ctrl.get_green_light_extension(),
                self.horizontal,
                self.vertical
            )
