"""Library with compatible bulb types.

Bulb Type detection:
ESP01_SHDW1C_31
ESP01 -- defines the module family (WiFi only bulb in this case)
SH -- Single Head light (most bulbs are single heads) / LED Strip
TW -- Tunable White - can only control CCT and dimming; no color
DW -- Dimmable White (most filament bulbs)
RGB -- Fullstack bulb
1C -- Specific to the hardware - defines PWM frequency + way of controlling CCT temperature
31 -- Related to the hardware revision
"""
import dataclasses
from enum import Enum
from typing import Optional


# TODO: make this frozen
@dataclasses.dataclass()
class Features:
    """Defines the supported features."""

    color: bool
    color_tmp: bool
    effect: bool
    brightness: bool


@dataclasses.dataclass(frozen=True)
class KelvinRange:
    """Defines the kelvin range."""

    max: int
    min: int


class BulbClass(Enum):
    """Bulb Types."""

    """Have Cool White and Warm White LEDs."""
    TW = "Tunable White"
    """Have only Dimmable white LEDs."""
    DW = "Dimmable White"
    """Have RGB LEDs."""
    RGB = "RGB Bulb"


# TODO: make this frozen
@dataclasses.dataclass()
class BulbType:
    """BulbType object to define functions and features of the bulb."""

    features: Features
    name: str
    kelvin_range: Optional[KelvinRange]
    bulb_type: BulbClass
