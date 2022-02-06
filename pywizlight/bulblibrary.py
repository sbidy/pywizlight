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
from typing import Optional, List

from pywizlight.exceptions import WizLightNotKnownBulb


@dataclasses.dataclass(frozen=True)
class Features:
    """Defines the supported features."""

    color: bool
    color_tmp: bool
    effect: bool
    brightness: bool


# RGB supports effects and tuneable white
RGB_FEATURES = Features(brightness=True, color=True, effect=True, color_tmp=True)

# TODO: TW supports effects but only "some"; improve the mapping to supported effects
TW_FEATURES = Features(brightness=True, color=False, effect=True, color_tmp=True)

# Dimmable white only supports brightness
DW_FEATURES = Features(brightness=True, color=False, effect=False, color_tmp=False)

# Socket supports only on/off
SOCKET_FEATURES = Features(brightness=False, color=False, effect=False, color_tmp=False)


@dataclasses.dataclass(frozen=True)
class KelvinRange:
    """Defines the kelvin range."""

    max: int
    min: int


class BulbClass(Enum):
    """Bulb Types."""

    TW = "Tunable White"
    """Have Cool White and Warm White LEDs."""
    DW = "Dimmable White"
    """Have only Dimmable white LEDs."""
    RGB = "RGB Bulb"
    """Have RGB LEDs."""
    SOCKET = "Socket"
    """Smart socket with only on/off."""


@dataclasses.dataclass(frozen=True)
class BulbType:
    """BulbType object to define functions and features of the bulb."""

    features: Features
    name: str
    kelvin_range: Optional[KelvinRange]
    bulb_type: BulbClass

    @staticmethod
    def from_data(module_name: str, kelvin_list: Optional[List[float]]) -> "BulbType":
        if kelvin_list:
            kelvin_range: Optional[KelvinRange] = KelvinRange(
                min=int(min(kelvin_list)), max=int(max(kelvin_list))
            )
        else:
            kelvin_range = None

        try:
            # parse the features from name
            _identifier = module_name.split("_")[1]
        # Throw exception if index can not be found
        except IndexError:
            raise WizLightNotKnownBulb("The bulb type can not be determined!")

        if "RGB" in _identifier:  # full RGB bulb
            features = RGB_FEATURES
            bulb_type = BulbClass.RGB
        elif "TW" in _identifier:  # Non RGB but tunable white bulb
            features = TW_FEATURES
            bulb_type = BulbClass.TW
        elif "SOCKET" in _identifier:  # A smart socket
            features = SOCKET_FEATURES
            bulb_type = BulbClass.SOCKET
        else:  # Plain brightness-only bulb
            features = DW_FEATURES
            bulb_type = BulbClass.DW

        return BulbType(
            bulb_type=bulb_type,
            name=module_name,
            features=features,
            kelvin_range=kelvin_range,
        )
