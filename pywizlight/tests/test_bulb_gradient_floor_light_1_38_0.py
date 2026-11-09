"""Tests for the Bulb API with a Gradient Floor Light."""

from typing import AsyncGenerator

import pytest

from pywizlight import PilotBuilder, SegmentStep, wizlight
from pywizlight.bulblibrary import BulbClass, BulbType, Features, KelvinRange
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture()
async def floor_light() -> AsyncGenerator[wizlight, None]:
    shutdown, port = await startup_bulb(
        module_name="ESP25_MHORGB_01", firmware_version="1.38.0"
    )
    bulb = wizlight(ip="127.0.0.1", port=port)
    yield bulb
    await bulb.async_close()
    shutdown()


@pytest.mark.asyncio
async def test_model_description(floor_light: wizlight) -> None:
    """Test fetching the model description for a gradient floor light."""
    assert await floor_light.get_bulbtype() == BulbType(
        features=Features(
            color=True, color_tmp=True, effect=True, brightness=True, dual_head=False
        ),
        name="ESP25_MHORGB_01",
        kelvin_range=KelvinRange(max=5500, min=2700),
        bulb_type=BulbClass.RGB,
        fw_version="1.38.0",
        white_channels=1,
        white_to_color_ratio=20,
        segment_count=18,
    )


@pytest.mark.asyncio
async def test_turn_on_segments(floor_light: wizlight) -> None:
    """Test turning on with segments."""
    await floor_light.turn_on(
        PilotBuilder(
            segments=[
                SegmentStep((255, 132, 0), 6),
                SegmentStep((187, 0, 255), 6),
                SegmentStep((149, 255, 0), 6),
            ]
        )
    )
    states = await floor_light.updateState()
    assert states and states[0]
    state = states[0]
    assert state.get_state() is True
    assert state.get_scene_id() == 258
    assert state.get_scene() == "Custom Mode 3"
    # The device never reports the steps back.
    assert "elm" not in state.pilotResult
