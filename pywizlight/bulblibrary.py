"""Library with compatible bulb types.

Bulb Type detection:
ESP01_SHDW1C_31
ESP01 -- defines the module family, WiFi only bulb this case
SH -- Single Head light / Most bulbs are singel heads / Stripes
TW -- Tunable White, as in can only control CCT and dimming, no color
DW -- Dimmable White / Most filament bulbs
RGB -- Fullstack bulb
1C -- Specific to the hardware -- defines PWM frequency + way of controlling CCT temperature
31 -- Related to the hardware revision
"""


from enum import Enum


class Features:
    """Defines the supported features."""

    color: bool
    color_tmp: bool
    effect: bool
    brightness: bool

    def __init__(
        self, color: bool, color_tmp: bool, effect: bool, brightness: bool
    ) -> None:
        """Init the features with type."""
        self.color = color
        self.color_tmp = color_tmp
        self.effect = effect
        self.brightness = brightness


class KelvinRange:
    """Deines the kelvin range."""

    max: int
    min: int

    def __init__(self, max: int, min: int) -> None:
        """Init for the kelvin range class."""
        self.max = max
        self.min = min


class BulbClass(Enum):
    """Bulb Types."""

    """Have Cool White and Warm White LEDs."""
    TW = "Tunabel White"
    """Have only Dimmable white LEDs."""
    DW = "Dimable White"
    """Have only Dimmable white LEDs."""
    RGB = "RGB Bulb"


class BulbType:
    """BulbType object to define functions and features of the bulb."""

    features: Features
    name: str
    filament_bulb: bool
    kelvin_range: KelvinRange
    bulb_type: BulbClass

    def __init__(
        self,
        features: Features,
        name: str,
        kelvin_range: KelvinRange,
        bulb_type: BulbClass,
    ) -> None:
        """Create a bulb object with different features."""
        self.features = features
        self.name = name
        self.kelvin_range = kelvin_range
        self.bulb_type = bulb_type
