from enum import Enum


class Lane(Enum):
    """Represents the direction of a traffic lane."""
    LEFT_TO_RIGHT = 1
    RIGHT_TO_LEFT = 2
    BOTTOM_TO_TOP = 3
    TOP_TO_BOTTOM = 4


class TrafficStatus(Enum):
    """Represents the traffic light state."""
    RED = 1
    GREEN = 2
    YELLOW = 3


class DoubleLane(Enum):
    """Represents pairings of opposing lanes."""
    HORIZONTAL = 1
    VERTICAL = 2
