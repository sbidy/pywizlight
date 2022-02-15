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
from typing import List, Optional

from pywizlight.exceptions import WizLightNotKnownBulb


@dataclasses.dataclass(frozen=True)
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

    TW = "Tunable White"
    """Have Cool White and Warm White LEDs."""
    DW = "Dimmable White"
    """Have only Dimmable white LEDs."""
    RGB = "RGB Tunable"
    """Have RGB LEDs."""
    SOCKET = "Socket"
    """Smart socket with only on/off."""


FEATURE_MAP = {
    # RGB supports effects and tuneable white
    BulbClass.RGB: Features(brightness=True, color=True, effect=True, color_tmp=True),
    # TODO: TW supports effects but only "some"; improve the mapping to supported effects
    BulbClass.TW: Features(brightness=True, color=False, effect=True, color_tmp=True),
    # Dimmable white only supports brightness and some basic effects
    BulbClass.DW: Features(brightness=True, color=False, effect=True, color_tmp=False),
    # Socket supports only on/off
    BulbClass.SOCKET: Features(
        brightness=False, color=False, effect=False, color_tmp=False
    ),
}


@dataclasses.dataclass(frozen=True)
class BulbType:
    """BulbType object to define functions and features of the bulb."""

    features: Features
    name: str
    kelvin_range: Optional[KelvinRange]
    bulb_type: BulbClass
    fw_version: Optional[str]
    white_channels: Optional[int]
    white_to_color_ratio: Optional[int]

    @staticmethod
    def from_data(
        module_name: str,
        kelvin_list: Optional[List[float]],
        fw_version: Optional[str],
        white_channels: Optional[int],
        white_to_color_ratio: Optional[int],
    ) -> "BulbType":
        try:
            # parse the features from name
            _identifier = module_name.split("_")[1]
        # Throw exception if index can not be found
        except IndexError:
            raise WizLightNotKnownBulb(
                f"The bulb type could not be determined from the module name: {module_name}"
            )

        if "RGB" in _identifier:  # full RGB bulb
            bulb_type = BulbClass.RGB
        elif "TW" in _identifier:  # Non RGB but tunable white bulb
            bulb_type = BulbClass.TW
        elif "SOCKET" in _identifier:  # A smart socket
            bulb_type = BulbClass.SOCKET
        else:  # Plain brightness-only bulb
            bulb_type = BulbClass.DW

        if kelvin_list:
            kelvin_range: Optional[KelvinRange] = KelvinRange(
                min=int(min(kelvin_list)), max=int(max(kelvin_list))
            )
        elif bulb_type in (BulbClass.RGB, BulbClass.TW):
            raise WizLightNotKnownBulb(
                f"Unable to determine required kelvin range for a {bulb_type.value} device"
            )
        else:
            kelvin_range = None

        features = FEATURE_MAP[bulb_type]

        return BulbType(
            bulb_type=bulb_type,
            name=module_name,
            features=features,
            kelvin_range=kelvin_range,
            fw_version=fw_version,
            white_channels=white_channels,
            white_to_color_ratio=white_to_color_ratio,
        )
