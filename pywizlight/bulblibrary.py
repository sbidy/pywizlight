"""Library with compatible bulb types."""


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


class BulbType:
    """BulbType object to define functions and features of the bulb."""

    features: Features
    name: str
    kelvin_range: KelvinRange

    def __init__(
        self, features: Features, name: str, kelvin_range: KelvinRange
    ) -> None:
        """Create a bulb object with different features."""
        self.features = features
        self.name = name
        self.kelvin_range = kelvin_range


class BulbLib:
    """Provides all existing bulbs."""

    BULBLIST = [
        # Only Brightness
        BulbType(
            name="ESP01_SHDW_01",
            features=Features(
                brightness=True, color=False, effect=False, color_tmp=False
            ),
            kelvin_range=KelvinRange(min=2200, max=6500),
        ),
        BulbType(
            name="ESP01_SHDW1_31",
            features=Features(
                brightness=True, color=False, effect=False, color_tmp=False
            ),
            kelvin_range=KelvinRange(min=2200, max=6500),
        ),
        BulbType(
            name="ESP03_SHDW1_01",
            features=Features(
                brightness=True, color=False, effect=False, color_tmp=False
            ),
            kelvin_range=KelvinRange(min=2200, max=6500),
        ),
        # Brightness and Effects
        BulbType(
            name="ESP06_SHDW9_01",
            features=Features(
                brightness=True, color=False, effect=True, color_tmp=False
            ),
            kelvin_range=KelvinRange(min=2200, max=6500),
        ),
        BulbType(
            name="ESP06_SHDW1_01",
            features=Features(
                brightness=True, color=False, effect=True, color_tmp=False
            ),
            kelvin_range=KelvinRange(min=2200, max=6500),
        ),
        # Brightness and Color Temp
        BulbType(
            name="ESP01_SHTW1C_31",
            features=Features(
                brightness=True, color=False, effect=False, color_tmp=True
            ),
            kelvin_range=KelvinRange(min=2200, max=6500),
        ),
        BulbType(
            name="ESP17_SHTW9_01",
            features=Features(
                brightness=True, color=False, effect=False, color_tmp=True
            ),
            kelvin_range=KelvinRange(min=2000, max=5000),
        ),
        # Brightness, Color Temp and Effect
        BulbType(
            name="ESP56_SHTW3_01",
            features=Features(
                brightness=True, color=False, effect=True, color_tmp=True
            ),
            kelvin_range=KelvinRange(min=2200, max=6500),
        ),
        BulbType(
            name="ESP15_SHTW1_01I",
            features=Features(
                brightness=True, color=False, effect=True, color_tmp=True
            ),
            kelvin_range=KelvinRange(min=2200, max=6500),
        ),
        BulbType(
            name="ESP03_SHTW1C_01",
            features=Features(
                brightness=True, color=False, effect=True, color_tmp=True
            ),
            kelvin_range=KelvinRange(min=2700, max=6500),
        ),
        BulbType(
            name="ESP03_SHTW1W_01",
            features=Features(
                brightness=True, color=False, effect=True, color_tmp=True
            ),
            kelvin_range=KelvinRange(min=2700, max=6500),
        ),
        # Brightness, Color Temp, Color and Effect / all features
        BulbType(
            name="ESP01_SHRGB1C_31",
            features=Features(brightness=True, color=True, effect=True, color_tmp=True),
            kelvin_range=KelvinRange(min=2200, max=6500),
        ),
        BulbType(
            name="ESP01_SHRGB3_01",
            features=Features(brightness=True, color=True, effect=True, color_tmp=True),
            kelvin_range=KelvinRange(min=2200, max=6500),
        ),
        # Test device
        BulbType(
            name="ESP01_SHRGB_03",
            features=Features(brightness=True, color=True, effect=True, color_tmp=True),
            kelvin_range=KelvinRange(min=2700, max=6500),
        ),
        BulbType(
            name="ESP03_SHRGBP_31",
            features=Features(brightness=True, color=True, effect=True, color_tmp=True),
            kelvin_range=KelvinRange(min=2000, max=6500),
        ),
        BulbType(
            name="ESP03_SHRGB1C_01",
            features=Features(brightness=True, color=True, effect=True, color_tmp=True),
            kelvin_range=KelvinRange(min=2200, max=6500),
        ),
        BulbType(
            name="ESP03_SHRGB1W_01",
            features=Features(brightness=True, color=True, effect=True, color_tmp=True),
            kelvin_range=KelvinRange(min=2200, max=6500),
        ),
        BulbType(
            name="ESP03_SHRGB3_01ABI",
            features=Features(brightness=True, color=True, effect=True, color_tmp=True),
            kelvin_range=KelvinRange(min=2200, max=6500),
        ),
        BulbType(
            name="ESP15_SHRGB1S_01I",
            features=Features(brightness=True, color=True, effect=True, color_tmp=True),
            kelvin_range=KelvinRange(min=2200, max=6500),
        ),
        BulbType(
            name="ESP14_SHRGB1C_01",
            features=Features(brightness=True, color=True, effect=True, color_tmp=True),
            kelvin_range=KelvinRange(min=2200, max=6500),
        ),
    ]

    def getBulbList(self) -> list:
        """Retrun the list of known bulbs as BulbType list."""
        return self.BULBLIST
