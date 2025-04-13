import numpy as np

# Centralized configuration for the Fuzzy Traffic Control Simulator
Config = {

    # Vehicle-related parameters
    'vehicle': {
        'speed': 5,
        'safe_distance': 5,
        'body_length': 30,
        'body_width': 20,
        'safe_spawn_factor': 1.1
    },

    # Simulator environment settings
    'simulator': {
        'screen_width': 800,
        'screen_height': 800,
        'bumper_distance': 5,
        'spawn_rate': {  # spawn intervals in milliseconds
            'fast': 400,
            'medium': 1500,
            'slow': 3500
        },
        'frame_rate': 30,
        'gap_between_traffic_switch': 2,      # seconds of delay between traffic light switches
        'moving_averages_period': 1,          # in seconds for statistics smoothing
        'static_duration': 1,                 # minimum duration before next change
        'seconds_before_extension': 1,        # delay before applying fuzzy extension
        'fuzzy_notification_duration': 5      # time to display fuzzy extension notification
    },

    # Color palette used across UI and simulation
    'colors': {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'dark_gray': (169, 169, 169),
        'traffic_yellow': (250, 210, 1),
        'lane_marker': (255, 255, 255),  # renamed 'traffic_yelloww'
        'traffic_green': (34, 139, 94),
        'traffic_red': (184, 29, 19),
        'red': (255, 0, 0),
        'yellow': (255, 255, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255)  # added for fuzzy button outline
    },

    # Traffic light timing and layout
    'traffic_light': {
        'red_light_duration': 10,         # in seconds
        'yellow_light_duration': 1.5,     # in seconds
        'green_light_duration': 10,       # in seconds
        'distance_from_center': (40, 10), # (x_offset, y_offset)
        'body_height': 30,
        'body_width': 20
    },

    # Background layout settings for roads, markings, buildings
    'background': {
        'road_marking_width': 2,
        'road_marking_alternate_lengths': (20, 10),  # line length, spacing
        'road_marking_gap_from_yellow_box': 50,
        'yellow_box_junction': (50, 50, 50, 50),  # top, right, bottom, left
        'building': (150, 150, 0, 0)  # width, height, not used for layout sides
    },

    # Fuzzy logic system configuration
    'fuzzy': {
        'range': {
            'behind_red_light': np.arange(-4, 17, 1),
            'arriving_green_light': np.arange(-4, 17, 1),
            'extension': np.arange(0, 21, 1)
        },
        'membership_function': {
            'behind_red_light': {
                'few': [0, 0, 3],
                'small': [0, 3, 6],
                'medium': [3, 6, 9],
                'many': [6, 9, 12]
            },
            'arriving_green_light': {
                'few': [0, 0, 3],
                'small': [0, 3, 6],
                'medium': [3, 6, 9],
                'many': [6, 9, 12]
            },
            'extension': {
                'zero': [0, 0, 0],
                'short': [0, 2, 4],
                'medium': [2, 4, 6],
                'long': [4, 6, 8]
            }
        }
    }
}
