"""Tests for the Bulb API."""
import pytest

from pywizlight import SCENES, PilotBuilder, wizlight
from pywizlight.discovery import discover_lights
from pywizlight.exceptions import WizLightTimeOutError
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture(scope="module")
def startup_fake_bulb(request: pytest.FixtureRequest) -> None:
    shutdown = startup_bulb(module_name="ESP01_SHRGB_03")
    request.addfinalizer(shutdown)


@pytest.fixture()
def correct_bulb(startup_fake_bulb: None) -> wizlight:
    return wizlight(ip="127.0.0.1")


@pytest.fixture()
def bad_bulb() -> wizlight:
    return wizlight(ip="1.1.1.1")


# Non-Error states - PilotBuilder - Turn On
@pytest.mark.asyncio
async def test_Bulb_Discovery(correct_bulb: wizlight) -> None:
    """Test discovery function."""
    bulbs = await discover_lights(broadcast_space="192.168.178.255")
    for bulb in bulbs:
        state = await bulb.updateState()
        assert state and state.get_state() is False


@pytest.mark.asyncio
async def test_PilotBuilder_state(correct_bulb: wizlight) -> None:
    """Test State."""
    state = await correct_bulb.updateState()
    assert state and state.get_state() is False


@pytest.mark.asyncio
async def test_PilotBuilder_colortemp(correct_bulb: wizlight) -> None:
    """Test Color Temp."""
    await correct_bulb.turn_on(PilotBuilder(colortemp=2800))
    state = await correct_bulb.updateState()

    assert state and state.get_colortemp() == 2800


@pytest.mark.asyncio
async def test_PilotBuilder_brightness(correct_bulb: wizlight) -> None:
    """Test Brightness."""
    await correct_bulb.turn_on(PilotBuilder(brightness=10))
    state = await correct_bulb.updateState()
    # 10% == 26 in Hex
    assert state and state.get_brightness() == 26


@pytest.mark.asyncio
async def test_PilotBuilder_warm_wite(correct_bulb: wizlight) -> None:
    """Test Warm White."""
    await correct_bulb.turn_on(PilotBuilder(warm_white=255))
    state = await correct_bulb.updateState()

    assert state and state.get_warm_white() == 255


@pytest.mark.asyncio
async def test_PilotBuilder_cold_white(correct_bulb: wizlight) -> None:
    """Test Cold White."""
    await correct_bulb.turn_on(PilotBuilder(cold_white=255))
    state = await correct_bulb.updateState()

    assert state and state.get_cold_white() == 255


@pytest.mark.asyncio
async def test_PilotBuilder_rgb(correct_bulb: wizlight) -> None:
    """Test RGB Value."""
    await correct_bulb.turn_on(PilotBuilder(rgb=(0, 128, 255)))
    state = await correct_bulb.updateState()

    assert state and state.get_rgb() == (0, 127, 255)


@pytest.mark.asyncio
async def test_PilotBuilder_scene(correct_bulb: wizlight) -> None:
    """Test Screen."""
    await correct_bulb.turn_on(PilotBuilder(scene=1))
    state = await correct_bulb.updateState()

    assert state and state.get_scene() == SCENES[1]


# ------ Error states -------------------------------------
@pytest.mark.asyncio
async def test_error_PilotBuilder_brightness(correct_bulb: wizlight) -> None:
    """Error Brightness."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(brightness=500))


@pytest.mark.asyncio
async def test_error_PilotBuilder_warm_wite(correct_bulb: wizlight) -> None:
    """Error Warm White."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(warm_white=300))
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(warm_white=-1))


@pytest.mark.asyncio
async def test_error_PilotBuilder_cold_white_upper(correct_bulb: wizlight) -> None:
    """Error Cold White."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(cold_white=300))


@pytest.mark.asyncio
async def test_error_PilotBuilder_cold_white_lower(correct_bulb: wizlight) -> None:
    """Error Cold White."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(cold_white=-1))


@pytest.mark.asyncio
async def test_error_PilotBuilder_r(correct_bulb: wizlight) -> None:
    """Error Red Value."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(rgb=(300, 0, 0)))


@pytest.mark.asyncio
async def test_error_PilotBuilder_green(correct_bulb: wizlight) -> None:
    """Error Green Value."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(rgb=(0, 300, 0)))


@pytest.mark.asyncio
async def test_error_PilotBuilder_blue(correct_bulb: wizlight) -> None:
    """Error Blue Value."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(rgb=(0, 0, 300)))


@pytest.mark.asyncio
async def test_error_PilotBuilder_scene(correct_bulb: wizlight) -> None:
    """Error Screen."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(scene=532))


# Error states / Timout
@pytest.mark.asyncio
async def test_timeout(bad_bulb: wizlight) -> None:
    """Test the timout exception after."""
    with pytest.raises(WizLightTimeOutError):
        await bad_bulb.getBulbConfig()


@pytest.mark.asyncio
async def test_timeout_PilotBuilder(bad_bulb: wizlight) -> None:
    """Test Timout for Result."""
    # check if the bulb state it given as bool - mock ?
    with pytest.raises(WizLightTimeOutError):
        await bad_bulb.turn_on(PilotBuilder(brightness=255))
