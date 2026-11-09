"""Tests for per-segment color."""

from typing import Optional

import pytest

from pywizlight import PilotBuilder
from pywizlight.bulblibrary import BulbType
from pywizlight.segments import SegmentStep

RED = (255, 0, 0)
BLUE = (0, 0, 255)


def test_pilot_builder_segments() -> None:
    """Test the setPilot message for segments."""
    builder = PilotBuilder(
        segments=[SegmentStep(RED, 9, brightness=40), SegmentStep(BLUE, 9)],
        brightness=128,
    )
    assert builder.set_pilot_message(state=True) == {
        "method": "setPilot",
        "params": {
            "sceneId": 258,
            "elm": {
                "modifier": 100,
                "support": 17,
                "steps": [
                    [0, 255, 0, 0, 0, 0, 0, 40, 0, 0, 0, 0, 9],
                    [0, 0, 0, 255, 0, 0, 0, 100, 0, 0, 0, 0, 9],
                ],
            },
            "dimming": 50,
            "state": True,
        },
    }


def test_segment_colors() -> None:
    """Test neighbors with the same color are merged into one step."""
    builder = PilotBuilder(segment_colors=[RED] * 9 + [BLUE] * 9)
    expected = PilotBuilder(segments=[SegmentStep(RED, 9), SegmentStep(BLUE, 9)])
    assert builder.pilot_params == expected.pilot_params
    with pytest.raises(ValueError):
        PilotBuilder(segment_colors=[RED, BLUE] * 6 + [RED])  # 13 runs
    with pytest.raises(ValueError):
        PilotBuilder(segment_colors=[])
    with pytest.raises(ValueError):
        PilotBuilder(segment_colors=[RED], segments=[SegmentStep(RED)])


def test_invalid_segments() -> None:
    """Test segments the device cannot show are rejected."""
    with pytest.raises(ValueError):
        SegmentStep((256, 0, 0))
    with pytest.raises(ValueError):
        SegmentStep(RED, width=0)
    with pytest.raises(ValueError):
        SegmentStep(RED, brightness=101)
    with pytest.raises(ValueError):
        PilotBuilder(segments=[])
    with pytest.raises(ValueError):
        PilotBuilder(segments=[SegmentStep(RED)] * 13)
    with pytest.raises(ValueError):
        PilotBuilder(segments=[SegmentStep(RED)], rgb=BLUE)


def _segment_count(module_name: str, sw_head: Optional[int]) -> Optional[int]:
    bulb_type = BulbType.from_data(
        module_name, [2700, 6500], "1.38.0", 1, 20, None, None, sw_head=sw_head
    )
    return bulb_type.segment_count


def test_segment_count() -> None:
    """Test only color lights with more than one head get a segment count."""
    assert _segment_count("ESP25_SHRGB_01", 0) is None
    assert _segment_count("ESP25_SHRGB_01", None) is None
    assert _segment_count("ESP20_DHRGB_01", 2) is None
    assert _segment_count("ESP21_SHTW_01", 18) is None
