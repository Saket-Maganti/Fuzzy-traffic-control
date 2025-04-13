import pygame
import os
from src.Common import DoubleLane, Lane
from src.Config import Config


class BackgroundController:
    def __init__(self, surface, traffic_lights):
        self.surface = surface
        self.traffic_lights = traffic_lights

        self.screen_height = Config['simulator']['screen_height']
        self.screen_width = Config['simulator']['screen_width']

        colors = Config['colors']
        self.black = colors['black']
        self.red = colors['red']
        self.white = colors['white']
        self.blue = colors.get('blue', (0, 0, 255))  # fallback if not defined

        self.spawn_rate = {
            DoubleLane.Horizontal: {'slow': True, 'medium': False, 'fast': False},
            DoubleLane.Vertical: {'slow': True, 'medium': False, 'fast': False}
        }

        self.spawn_rate_buttons = {
            lane: {rate: None for rate in ['slow', 'medium', 'fast']}
            for lane in [DoubleLane.Horizontal, DoubleLane.Vertical]
        }

        self.switch_traffic_button = None
        self.fuzzy_button = None

    def _load_scaled_image(self, *rel_path_parts, size):
        path = os.path.join(os.getcwd(), 'images', *rel_path_parts)
        image = pygame.image.load(path)
        return pygame.transform.scale(image, size)

    def set_spawn_rate(self, double_lane: DoubleLane, target_rate):
        for rate in ['slow', 'medium', 'fast']:
            self.spawn_rate[double_lane][rate] = (target_rate == rate)

    def get_spawn_rate(self, double_lane: DoubleLane):
        for rate in ['slow', 'medium', 'fast']:
            if self.spawn_rate[double_lane][rate]:
                return rate
        raise Exception('None of slow, medium, fast is true!')

    def refresh_screen(self):
        self.surface.fill(self.black)

    def draw_spawn_rate_buttons(self):
        normal_font = pygame.font.SysFont('Sans-serif', 25)
        underline_font = pygame.font.SysFont('Sans-serif', 25)
        underline_font.set_underline(True)

        def draw_buttons(label, y_offset, lane):
            self.surface.blit(normal_font.render(label, True, self.white), (5, y_offset))
            fonts = [normal_font] * 3
            colors = [self.white] * 3
            rates = ['slow', 'medium', 'fast']

            for i, rate in enumerate(rates):
                if self.spawn_rate[lane][rate]:
                    fonts[i] = underline_font
                    colors[i] = self.red

            x_pos = 200
            for i, rate in enumerate(rates):
                rendered = fonts[i].render(rate.capitalize() + ' ', True, colors[i])
                self.spawn_rate_buttons[lane][rate] = self.surface.blit(rendered, (x_pos, y_offset))
                x_pos += 60

        draw_buttons('Horizontal Speed:', 25, DoubleLane.Horizontal)
        draw_buttons('Spawn Rate (Vertical):', 45, DoubleLane.Vertical)

    def draw_moving_averages(self, moving_averages):
        font = pygame.font.SysFont('Sans-serif', 25)
        self.surface.blit(font.render('Vehicles behind traffic (Horizontal):', True, self.white), (5, 65))
        self.surface.blit(font.render(f'{moving_averages[Lane.left_to_right]:.2f}', True, self.white), (320, 65))
        self.surface.blit(font.render('Vehicles behind traffic (Vertical):', True, self.white), (5, 85))
        self.surface.blit(font.render(f'{moving_averages[Lane.top_to_bottom]:.2f}', True, self.white), (320, 85))

    def draw_vehicle_count(self, total):
        font = pygame.font.SysFont('Sans-serif', 25)
        self.surface.blit(font.render(f'Total Vehicles: {total}', True, self.white), (5, 5))

    def draw_road_markings(self):
        cfg = Config['background']
        bumper = Config['simulator']['bumper_distance']
        body_width = Config['vehicle']['body_width']
        mark_width = cfg['road_marking_width']
        mark_len, mark_gap = cfg['road_marking_alternate_lengths']
        yb_top, yb_left, yb_bottom, yb_right = cfg['yellow_box_junction']
        gap = cfg['road_marking_gap_from_yellow_box']
        color = Config['colors']['traffic_yelloww']

        # yellow box junction
        yellow_box = self._load_scaled_image('junction', 'yellow_box_junction.png', size=(yb_left + yb_right, yb_top + yb_bottom))
        self.surface.blit(yellow_box, (self.screen_width / 2 - yb_left, self.screen_height / 2 - yb_top))

        # buildings
        for name, pos in [
            ('b4.jpg', (8, 225)), ('b4.jpg', (168, 225)), ('b3.jpg', (460, 225)), ('b3.jpg', (620, 225)),
            ('b1.jpg', (self.screen_width - yb_left, 470)), ('b1.jpg', (self.screen_width - yb_left - 80, 470)),
            ('b1.jpg', (self.screen_width - yb_left - 230, 470)), ('b4.jpg', (8, 470)), ('b4.jpg', (8, 550)),
            ('b4.jpg', (8, 710)), ('b4.jpg', (179, 470)), ('b4.jpg', (179, 550)), ('b4.jpg', (179, 710))
        ]:
            building = self._load_scaled_image('buildings', name, size=(yb_left + yb_right, yb_top + yb_bottom))
            self.surface.blit(building, pos)

        # roads and pool
        for img, pos in [('road1.png', (378, 0)), ('road1.png', (378, 450)), ('road3.png', (0, 380)), ('road3.png', (450, 380)), ('pool.png', (400, 0))]:
            asset = self._load_scaled_image('buildings', img, size=(yb_left + yb_right, yb_top + yb_bottom))
            self.surface.blit(asset, pos)

        # top-bottom markings
        for x in [
            self.screen_width / 2 - bumper - body_width / 2 - mark_width / 2,
            self.screen_width / 2 + bumper + body_width / 2 - mark_width / 2
        ]:
            y = self.screen_height / 2 - yb_top - mark_len - mark_gap
            while y >= 0:
                pygame.draw.rect(self.surface, color, (x, y, mark_width, mark_len))
                y -= mark_len + mark_gap
            y = self.screen_height / 2 + yb_bottom + gap
            while y <= self.screen_height:
                pygame.draw.rect(self.surface, color, (x, y, mark_width, mark_len))
                y += mark_len + mark_gap

        # left-right markings
        for y in [
            self.screen_height / 2 - bumper - body_width / 2 - mark_width / 2,
            self.screen_height / 2 + bumper + body_width / 2 - mark_width / 2
        ]:
            x = self.screen_width / 2 - yb_left - mark_len - gap
            while x >= 0:
                pygame.draw.rect(self.surface, color, (x, y, mark_len, mark_width))
                x -= mark_len + mark_gap
            x = self.screen_width / 2 + yb_right + gap
            while x <= self.screen_width:
                pygame.draw.rect(self.surface, color, (x, y, mark_len, mark_width))
                x += mark_len + mark_gap

    def within_boundary(self, x, y):
        return 0 <= x <= self.screen_width and 0 <= y <= self.screen_height

    def draw_switch_traffic_button(self):
        font = pygame.font.SysFont('Comic Sans MS', 16)
        text = font.render('Switch', True, self.red)
        rect = self.surface.blit(text, (self.screen_width - 100, 20))
        pygame.draw.rect(self.surface, self.red, (rect.left - 5, rect.top - 5, rect.width + 10, rect.height + 10), 3)
        self.switch_traffic_button = rect

    def draw_fuzzy_button(self):
        font = pygame.font.SysFont('Comic Sans MS', 16)
        text = font.render('Calculate Fuzzy', True, self.red)
        rect = self.surface.blit(text, (self.screen_width - 150, 90))
        pygame.draw.rect(self.surface, self.blue, (rect.left - 5, rect.top - 5, rect.width + 10, rect.height + 10), 3)
        self.fuzzy_button = rect

    def draw_fuzzy_score(self, fuzzy_score, current_lane: DoubleLane):
        font = pygame.font.SysFont('Sans-serif', 20)
        lane_label = 'Horizontal' if current_lane == DoubleLane.Vertical else 'Vertical'
        self.surface.blit(font.render(f'Fuzzy Green Light Ext. ({lane_label} Lane): ', True, self.white), (5, 105))
        score = '-' if fuzzy_score is None else f'{fuzzy_score:.2f}s'
        self.surface.blit(font.render(score, True, self.white), (320, 105))

    def draw_extension_notification(self, extension, horizontal, vertical):
        font = pygame.font.SysFont('Sans-serif', 20)
        green = Config['colors']['traffic_green']
        self.surface.blit(font.render('Vehicle behind Traffic Light', True, green), (5, 125))
        self.surface.blit(font.render(f'     Horizontal : {horizontal:.1f}', True, green), (5, 145))
        self.surface.blit(font.render(f'     Vertical : {vertical:.1f}', True, green), (5, 165))
        self.surface.blit(font.render(f'Green light is extended by {extension:.1f}!', True, green), (5, 185))

    def draw_light_durations(self, green_light_extension):
        font = pygame.font.SysFont('Sans-serif', 20)
        traffic = Config['traffic_light']
        pygame.draw.circle(self.surface, Config['colors']['traffic_red'], (self.screen_width - 180, 16), 8)
        self.surface.blit(font.render(f'Duration: {traffic["red_light_duration"]:.1f}', True, self.black),
                          (self.screen_width - 160, 5))

        pygame.draw.circle(self.surface, Config['colors']['traffic_yellow'], (self.screen_width - 180, 36), 8)
        self.surface.blit(font.render(f'Duration: {traffic["yellow_light_duration"]:.1f}', True, self.black),
                          (self.screen_width - 160, 25))

        pygame.draw.circle(self.surface, Config['colors']['traffic_green'], (self.screen_width - 180, 56), 8)
        if green_light_extension > 0:
            text = f'Duration: {traffic["green_light_duration"]:.1f} + {green_light_extension:.1f}'
        else:
            text = f'Duration: {traffic["green_light_duration"]:.1f}'
        self.surface.blit(font.render(text, True, self.black), (self.screen_width - 160, 45))
