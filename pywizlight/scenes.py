"""Definition of the supported bulb effects."""

from typing import Dict, Iterable, List, cast

from pywizlight.bulblibrary import BulbClass

# Ordered by name and not by ID
SCENES = {
    35: "Alarm",
    10: "Bedtime",
    29: "Candlelight",
    27: "Christmas",
    6: "Cozy",
    13: "Cool white",
    12: "Daylight",
    33: "Diwali",
    23: "Deep dive",
    22: "Fall",
    5: "Fireplace",
    7: "Forest",
    15: "Focus",
    30: "Golden white",
    28: "Halloween",
    24: "Jungle",
    25: "Mojito",
    14: "Night light",
    1: "Ocean",
    4: "Party",
    31: "Pulse",
    8: "Pastel colors",
    2: "Romance",
    16: "Relax",
    3: "Sunset",
    20: "Spring",
    21: "Summer",
    32: "Steampunk",
    17: "True colors",
    18: "TV time",
    34: "White",
    9: "Wake-up",
    11: "Warm white",
    1000: "Rhythm",
}
SCENE_NAME_TO_ID = {scene_name: scene_id for (scene_id, scene_name) in SCENES.items()}
TW_SCENES = [6, 9, 10, 11, 12, 13, 14, 15, 16, 18, 29, 30, 31, 32, 33, 35]
DW_SCENES = [9, 10, 14, 29, 31, 32, 34, 35]

SCENES_BY_CLASS: Dict[BulbClass, List[str]] = {
    BulbClass.RGB: list(cast(Iterable, SCENES.values())),
    BulbClass.TW: [SCENES[key] for key in TW_SCENES],
    BulbClass.DW: [SCENES[key] for key in DW_SCENES],
}


def get_id_from_scene_name(scene: str) -> int:
    """Return the id of an given scene name.

    :param scene: Name of the scene
    :raises ValueError: Return if not in scene list
    :return: ID of the scene
    """
    scene_id = SCENE_NAME_TO_ID.get(scene)
    if not scene_id:
        raise ValueError(f"Scene '{scene}' not in scene list.")
    return scene_id
