"""Per-segment color for lights with addressable segments.

WiZ does not document the format; see "Per-segment color" in the README.
"""

import dataclasses
from typing import Any, Dict, List, Sequence, Tuple, cast

MAX_SEGMENT_STEPS = 12
"""The most steps a device accepts in one request."""

SEGMENT_SCENE_ID = 258
"""Custom mode slot the steps are written to ("Custom Mode 3")."""

_ELM_MODIFIER_STATIC = 100
_ELM_SUPPORT = 17


def _is_int(value: Any) -> bool:
    """Return True for an int that is not a bool."""
    return isinstance(value, int) and not isinstance(value, bool)


@dataclasses.dataclass(frozen=True)
class SegmentStep:
    """A run of adjacent segments that show one color."""

    rgb: Tuple[int, int, int]
    width: int = 1  # number of segments
    brightness: int = 100  # percent

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
    """Turn one color per segment into steps, merging neighbors that match."""
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
