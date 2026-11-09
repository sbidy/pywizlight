"""Per-segment color for WiZ devices with individually addressable segments.

Devices such as the Gradient Floor Light and RGBIC light strips accept a list
of color steps in a custom mode slot. WiZ does not document the format; this
is what has been confirmed on an ESP25_MHORGB_01 running firmware 1.38.0:

    {"method": "setPilot", "params": {"sceneId": 258, "elm": {
        "modifier": 100, "support": 17,
        "steps": [[0, R, G, B, 0, 0, 0, DIM, 0, 0, 0, 0, WIDTH], ...]}}}

- Steps are laid down from the start of the device (the bottom of the floor
  light), each covering WIDTH segments. Segments past the sum of the widths
  stay dark.
- DIM is the brightness of the step in percent. 0 is dark.
- The device accepts at most 12 steps and answers 13 or more with -32602.
- getPilot reports sceneId 258 afterwards but never returns the steps.
- A plain dimming change keeps the steps; a color or temperature leaves them.
- modifier 100 with support 17 shows the colors as given. What the other
  values and the zero fields in each step mean is not known.
"""

import dataclasses
from typing import Any, Dict, List, Sequence, Tuple, cast

MAX_SEGMENT_STEPS = 12
"""The most steps a device accepts in one request."""

SEGMENT_SCENE_ID = 258
"""Custom mode slot the steps are written to ("Custom Mode 3").

On an RGBIC strip, a slot holding a light mode saved in the WiZ app was
reported to play that mode and ignore the steps, so this needs to be a slot
the app has left empty.
"""

_ELM_MODIFIER_STATIC = 100
_ELM_SUPPORT = 17


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


@dataclasses.dataclass(frozen=True)
class SegmentStep:
    """A run of adjacent segments that show one color.

    :param rgb: red, green and blue, each 0-255
    :param width: how many segments the step covers, at least 1
    :param brightness: brightness of the step in percent, 0-100
    """

    rgb: Tuple[int, int, int]
    width: int = 1
    brightness: int = 100

    def __post_init__(self) -> None:
        """Reject values the device cannot show."""
        if len(self.rgb) != 3 or not all(_is_int(c) for c in self.rgb):
            raise ValueError("rgb must be three integers")
        if not all(0 <= c <= 255 for c in self.rgb):
            raise ValueError("rgb values must be between 0 and 255")
        if not _is_int(self.width) or self.width < 1:
            raise ValueError("width must be an integer of at least 1")
        if not _is_int(self.brightness) or not 0 <= self.brightness <= 100:
            raise ValueError("brightness must be an integer between 0 and 100")

    def as_elm_step(self) -> List[int]:
        """Return the step as the device expects it."""
        red, green, blue = self.rgb
        return [0, red, green, blue, 0, 0, 0, self.brightness, 0, 0, 0, 0, self.width]


def build_elm(steps: Sequence[SegmentStep]) -> Dict[str, Any]:
    """Return the elm object for a setPilot request."""
    if not 1 <= len(steps) <= MAX_SEGMENT_STEPS:
        raise ValueError(
            f"Between 1 and {MAX_SEGMENT_STEPS} segment steps are supported, "
            f"got {len(steps)}"
        )
    return {
        "modifier": _ELM_MODIFIER_STATIC,
        "support": _ELM_SUPPORT,
        "steps": [step.as_elm_step() for step in steps],
    }


def steps_from_colors(colors: Sequence[Tuple[int, int, int]]) -> List[SegmentStep]:
    """Turn one color per segment into steps, merging neighbors that match.

    The device takes at most 12 steps, so a list with more than 12 runs of
    different colors cannot be shown and raises ValueError.
    """
    steps: List[SegmentStep] = []
    for color in colors:
        rgb = cast(Tuple[int, int, int], tuple(color))
        if steps and steps[-1].rgb == rgb:
            last = steps[-1]
            steps[-1] = dataclasses.replace(last, width=last.width + 1)
        else:
            steps.append(SegmentStep(rgb=rgb))
    if not steps:
        raise ValueError("At least one segment color is required")
    if len(steps) > MAX_SEGMENT_STEPS:
        raise ValueError(
            f"{len(steps)} runs of different colors; the device shows at most "
            f"{MAX_SEGMENT_STEPS}"
        )
    return steps
