"""Tests for per-segment color steps."""

from typing import Any, Dict, Tuple

import pytest

from pywizlight import PilotBuilder, SegmentStep, steps_from_colors
from pywizlight.bulblibrary import BulbType
from pywizlight.segments import MAX_SEGMENT_STEPS, SEGMENT_SCENE_ID, build_elm

RED = (255, 0, 0)
BLUE = (0, 0, 255)


def test_step_layout() -> None:
    """Test the position of color, brightness and width in a step."""
    step = SegmentStep((255, 132, 0), width=6, brightness=40)
    assert step.as_elm_step() == [0, 255, 132, 0, 0, 0, 0, 40, 0, 0, 0, 0, 6]


def test_step_defaults() -> None:
    """Test the step defaults."""
    assert SegmentStep(RED).as_elm_step() == [0, 255, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 1]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"rgb": (256, 0, 0)},
        {"rgb": (0, -1, 0)},
        {"rgb": (0, 0)},
        {"rgb": (0, 0, 0, 0)},
        {"rgb": (0.5, 0, 0)},
        {"rgb": (True, 0, 0)},
        {"rgb": RED, "width": 0},
        {"rgb": RED, "width": 1.5},
        {"rgb": RED, "brightness": 101},
        {"rgb": RED, "brightness": -1},
        {"rgb": RED, "brightness": 50.0},
    ],
)
def test_step_rejects_bad_values(kwargs: Dict[str, Any]) -> None:
    """Test values the device cannot show are rejected."""
    with pytest.raises(ValueError):
        SegmentStep(**kwargs)


def test_build_elm() -> None:
    """Test building the elm object."""
    elm = build_elm([SegmentStep(RED, 9), SegmentStep(BLUE, 9)])
    assert elm == {
        "modifier": 100,
        "support": 17,
        "steps": [
            [0, 255, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 9],
            [0, 0, 0, 255, 0, 0, 0, 100, 0, 0, 0, 0, 9],
        ],
    }


def test_build_elm_step_count() -> None:
    """Test the step count limits."""
    assert len(build_elm([SegmentStep(RED)] * MAX_SEGMENT_STEPS)["steps"]) == 12
    with pytest.raises(ValueError):
        build_elm([])
    with pytest.raises(ValueError):
        build_elm([SegmentStep(RED)] * (MAX_SEGMENT_STEPS + 1))


def test_steps_from_colors_merges_runs() -> None:
    """Test neighbors with the same color are merged."""
    assert steps_from_colors([RED] * 9 + [BLUE] * 9) == [
        SegmentStep(RED, 9),
        SegmentStep(BLUE, 9),
    ]


def test_steps_from_colors_accepts_lists() -> None:
    """Test colors given as lists."""
    assert steps_from_colors([[255, 0, 0], [255, 0, 0]]) == [  # type: ignore[list-item]
        SegmentStep(RED, 2)
    ]


def test_steps_from_colors_limits() -> None:
    """Test the limits of steps_from_colors."""
    alternating: Tuple[Tuple[int, int, int], ...] = (RED, BLUE) * 6
    assert len(steps_from_colors(alternating)) == 12
    with pytest.raises(ValueError):
        steps_from_colors(alternating + (RED,))
    with pytest.raises(ValueError):
        steps_from_colors([])
    with pytest.raises(ValueError):
        steps_from_colors([(300, 0, 0)])


def test_pilot_builder_segments() -> None:
    """Test the setPilot message for segments."""
    message = PilotBuilder(segments=[SegmentStep(RED, 18)]).set_pilot_message(
        state=True
    )
    assert message == {
        "method": "setPilot",
        "params": {
            "sceneId": SEGMENT_SCENE_ID,
            "elm": {
                "modifier": 100,
                "support": 17,
                "steps": [[0, 255, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 18]],
            },
            "state": True,
        },
    }


def test_pilot_builder_segments_with_brightness() -> None:
    """Test brightness with segments."""
    builder = PilotBuilder(segments=[SegmentStep(RED, 18)], brightness=128)
    assert builder.pilot_params["dimming"] == 50
    assert builder.pilot_params["sceneId"] == SEGMENT_SCENE_ID


@pytest.mark.parametrize(
    "kwargs",
    [
        {"rgb": RED},
        {"rgbw": (255, 0, 0, 0)},
        {"rgbww": (255, 0, 0, 0, 0)},
        {"hucolor": (0, 100)},
        {"colortemp": 2700},
        {"scene": 4},
        {"warm_white": 10},
        {"cold_white": 10},
    ],
)
def test_pilot_builder_segments_exclusive(kwargs: Dict[str, Any]) -> None:
    """Test segments cannot be combined with a color or scene."""
    with pytest.raises(ValueError):
        PilotBuilder(segments=[SegmentStep(RED)], **kwargs)


def test_pilot_builder_too_many_segments() -> None:
    """Test more than 12 steps are rejected."""
    with pytest.raises(ValueError):
        PilotBuilder(segments=[SegmentStep(RED)] * 13)


def _bulb_type(module_name: str, sw_head: Any) -> BulbType:
    return BulbType.from_data(
        module_name, [2700, 6500], "1.38.0", 1, 20, None, None, sw_head=sw_head
    )


@pytest.mark.parametrize(
    ("module_name", "sw_head", "expected"),
    [
        ("ESP25_MHORGB_01", 18, 18),
        ("ESP25_MHORGB_01", 17, 17),
        ("ESP25_SHRGB_01", 0, None),
        ("ESP25_SHRGB_01", None, None),
        ("ESP25_SHRGB_01", 1, None),
        ("ESP25_SHRGB_01", True, None),
        ("ESP25_SHRGB_01", "18", None),
        ("ESP20_DHRGB_01", 2, None),
        ("ESP21_SHTW_01", 18, None),
    ],
)
def test_segment_count(module_name: str, sw_head: Any, expected: Any) -> None:
    """Test the segment count from swHead."""
    assert _bulb_type(module_name, sw_head).segment_count == expected
