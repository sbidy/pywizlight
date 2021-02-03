"""Library with compatible bulb types."""

import json

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

    def __init__(self) -> None:
        with open(__file__ + "definitions/lights.json") as f:
            self.bulb_list = [ BulbType(
            name=i["name"],
            features=Features(
                brightness=i["features"]["brightness"], color=i["features"]["color"], effect=i["features"]["effect"], color_tmp=i["features"]["color_tmp"]
            ),
            kelvin_range=KelvinRange(min=i["kelvin_range"]["min"], max=i["kelvin_range"]["max"]),
        ) for i in json.load(f)]
        self.bulb_list = []


    def getBulbList(self) -> list:
        """Retrun the list of known bulbs as BulbType list."""
        return self.bulb_list
