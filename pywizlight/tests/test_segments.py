"""Tests for per-segment color steps."""

from typing import Any, Dict, Tuple

import pytest

from pywizlight import PilotBuilder, SegmentStep, steps_from_colors
from pywizlight.bulblibrary import BulbType
from pywizlight.segments import MAX_SEGMENT_STEPS, SEGMENT_SCENE_ID, build_elm

RED = (255, 0, 0)
BLUE = (0, 0, 255)


def test_step_layout() -> None:
    """A step puts color, brightness and width where the device reads them."""
    step = SegmentStep((255, 132, 0), width=6, brightness=40)
    assert step.as_elm_step() == [0, 255, 132, 0, 0, 0, 0, 40, 0, 0, 0, 0, 6]


def test_step_defaults() -> None:
    """A step covers one segment at full brightness by default."""
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
    """Values the device cannot show raise ValueError."""
    with pytest.raises(ValueError):
        SegmentStep(**kwargs)


def test_build_elm() -> None:
    """The elm object carries the static modifier and the steps in order."""
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
    """Between 1 and 12 steps are accepted."""
    assert len(build_elm([SegmentStep(RED)] * MAX_SEGMENT_STEPS)["steps"]) == 12
    with pytest.raises(ValueError):
        build_elm([])
    with pytest.raises(ValueError):
        build_elm([SegmentStep(RED)] * (MAX_SEGMENT_STEPS + 1))


def test_steps_from_colors_merges_runs() -> None:
    """Neighboring segments with the same color become one wider step."""
    assert steps_from_colors([RED] * 9 + [BLUE] * 9) == [
        SegmentStep(RED, 9),
        SegmentStep(BLUE, 9),
    ]


def test_steps_from_colors_accepts_lists() -> None:
    """Colors can be lists, as they arrive from JSON."""
    assert steps_from_colors([[255, 0, 0], [255, 0, 0]]) == [  # type: ignore[list-item]
        SegmentStep(RED, 2)
    ]


def test_steps_from_colors_limits() -> None:
    """Twelve runs fit; a thirteenth or an empty list does not."""
    alternating: Tuple[Tuple[int, int, int], ...] = (RED, BLUE) * 6
    assert len(steps_from_colors(alternating)) == 12
    with pytest.raises(ValueError):
        steps_from_colors(alternating + (RED,))
    with pytest.raises(ValueError):
        steps_from_colors([])
    with pytest.raises(ValueError):
        steps_from_colors([(300, 0, 0)])


def test_pilot_builder_segments() -> None:
    """Segments are written to the custom mode slot with the elm object."""
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
    """Brightness still sets the master dimming."""
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
    """Segments replace the color, so they cannot be mixed with one."""
    with pytest.raises(ValueError):
        PilotBuilder(segments=[SegmentStep(RED)], **kwargs)


def test_pilot_builder_too_many_segments() -> None:
    """More than 12 steps is rejected before anything is sent."""
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
    """Only color lights reporting more than one head get a segment count."""
    assert _bulb_type(module_name, sw_head).segment_count == expected
