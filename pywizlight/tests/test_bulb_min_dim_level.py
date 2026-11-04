"""Tests for clamping dimming to the bulb's minDimLevel."""

from typing import AsyncGenerator, Callable

import pytest

from pywizlight import PilotBuilder, wizlight
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture()
async def make_bulb() -> AsyncGenerator[Callable, None]:
    cleanups = []

    async def _make_bulb(module_name: str, firmware_version: str) -> wizlight:
        shutdown, port = await startup_bulb(
            module_name=module_name, firmware_version=firmware_version
        )
        bulb = wizlight(ip="127.0.0.1", port=port)
        cleanups.append((bulb, shutdown))
        return bulb

    yield _make_bulb
    for bulb, shutdown in cleanups:
        await bulb.async_close()
        shutdown()


async def _dimming(bulb: wizlight) -> int:
    states = await bulb.updateState()
    assert states and states[0]
    return states[0].pilotResult["dimming"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "module_name,firmware_version,expected",
    [
        ("ESP25_SHRGB_01", "1.38.0", 1),  # minDimLevel 1
        ("ESP24_SHRGB_01", "1.38.0", 10),  # minDimLevel 10
        ("ESP01_SHRGB_03", "1.25.0", 10),  # no minDimLevel reported
        ("ESP01_SHRGB1C_31", "1.17.1", 10),  # no getModelConfig
    ],
)
async def test_turn_on_clamps_dimming(
    make_bulb: Callable, module_name: str, firmware_version: str, expected: int
) -> None:
    """Test the lowest brightness is clamped to the bulb's minimum dimming."""
    bulb = await make_bulb(module_name, firmware_version)
    await bulb.turn_on(PilotBuilder(brightness=1))
    assert await _dimming(bulb) == expected


@pytest.mark.asyncio
async def test_turn_on_keeps_dimming_above_minimum(make_bulb: Callable) -> None:
    """Test brightness above the bulb's minimum dimming is sent unchanged."""
    bulb = await make_bulb("ESP24_SHRGB_01", "1.38.0")
    await bulb.turn_on(PilotBuilder(brightness=128))
    assert await _dimming(bulb) == 50


@pytest.mark.asyncio
async def test_turn_on_clamps_dimming_after_get_bulbtype(
    make_bulb: Callable,
) -> None:
    """Test the model config cached by get_bulbtype is used for clamping."""
    bulb = await make_bulb("ESP24_SHRGB_01", "1.38.0")
    await bulb.get_bulbtype()
    await bulb.turn_on(PilotBuilder(brightness=1))
    assert await _dimming(bulb) == 10


@pytest.mark.asyncio
async def test_set_state_clamps_dimming(make_bulb: Callable) -> None:
    """Test set_state clamps dimming to the bulb's minimum."""
    bulb = await make_bulb("ESP24_SHRGB_01", "1.38.0")
    await bulb.set_state(PilotBuilder(brightness=1))
    assert await _dimming(bulb) == 10
