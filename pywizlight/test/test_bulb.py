"""Tests for the Bulb API."""
import pytest

from pywizlight import wizlight, PilotBuilder, SCENES
from pywizlight.exceptions import WizLightTimeOutError


def pytest_namespace():
    """Define the global var."""
    return {"correct_bulb": wizlight, "bad_bulb": wizlight}


@pytest.fixture
def data():
    """Init the bad and good bulbs."""
    pytest.correct_bulb = wizlight(ip="192.168.178.95")
    pytest.bad_bulb = wizlight(ip="1.1.1.1")


@pytest.fixture(autouse=True)
async def run_after_tests():
    """Run after Testes."""
    yield
    await pytest.correct_bulb.turn_off()


# Non-Error states - PilotBuilder
@pytest.mark.asyncio
async def test_Bulb_Discovery():
    """Test discovery function."""
    bulbs = await wizlight.discover_lights(broadcast_space="192.168.178.255")
    state = await bulb.updateState()
    assert state.get_state() is False


@pytest.mark.asyncio
async def test_PilotBuilder_state(data):
    """Test State."""
    state = await pytest.correct_bulb.updateState()
    assert state.get_state() is False


@pytest.mark.asyncio
async def test_PilotBuilder_colortemp(data):
    """Test Color Temp."""
    await pytest.correct_bulb.turn_on(PilotBuilder(colortemp=2800))
    state = await pytest.correct_bulb.updateState()

    assert state.get_colortemp() == 2800


@pytest.mark.asyncio
async def test_PilotBuilder_brightness(data):
    """Test Brightness."""
    await pytest.correct_bulb.turn_on(PilotBuilder(brightness=10))
    state = await pytest.correct_bulb.updateState()
    # 10% == 26 in Hex
    assert state.get_brightness() == 26
    await pytest.correct_bulb.turn_off()


@pytest.mark.asyncio
async def test_PilotBuilder_warm_wite(data):
    """Test Warm White."""
    await pytest.correct_bulb.turn_on(PilotBuilder(warm_white=255))
    state = await pytest.correct_bulb.updateState()

    assert state.get_warm_white() == 255
    await pytest.correct_bulb.turn_off()


@pytest.mark.asyncio
async def test_PilotBuilder_cold_white(data):
    """Test Cold White."""
    await pytest.correct_bulb.turn_on(PilotBuilder(cold_white=255))
    state = await pytest.correct_bulb.updateState()

    assert state.get_cold_white() == 255
    await pytest.correct_bulb.turn_off()


@pytest.mark.asyncio
async def test_PilotBuilder_rgb(data):
    """Test RGB Value."""
    await pytest.correct_bulb.turn_on(PilotBuilder(rgb=(0, 128, 255)))
    state = await pytest.correct_bulb.updateState()

    assert state.get_rgb() == (0, 128, 255)
    await pytest.correct_bulb.turn_off()


@pytest.mark.asyncio
async def test_PilotBuilder_scene(data):
    """Test Screen."""
    await pytest.correct_bulb.turn_on(PilotBuilder(scene=1))
    state = await pytest.correct_bulb.updateState()

    assert state.get_scene() == SCENES[1]
    await pytest.correct_bulb.turn_off()


# ------ Error states -------------------------------------
@pytest.mark.asyncio
async def test_error_PilotBuilder_brightness(data):
    """Error Brightness."""
    with pytest.raises(ValueError):
        await pytest.correct_bulb.turn_on(PilotBuilder(brightness=500))


@pytest.mark.asyncio
async def test_error_PilotBuilder_warm_wite(data):
    """Error Warm White."""
    with pytest.raises(ValueError):
        await pytest.correct_bulb.turn_on(PilotBuilder(warm_white=300))
    with pytest.raises(ValueError):
        await pytest.correct_bulb.turn_on(PilotBuilder(warm_white=0))


@pytest.mark.asyncio
async def test_error_PilotBuilder_cold_white(data):
    """Error Cold White."""
    with pytest.raises(ValueError):
        await pytest.correct_bulb.turn_on(PilotBuilder(cold_white=300))
    with pytest.raises(ValueError):
        await pytest.correct_bulb.turn_on(PilotBuilder(cold_white=0))


@pytest.mark.asyncio
async def test_error_PilotBuilder_rgb(data):
    """Error RGB Value."""
    # Red
    with pytest.raises(ValueError):
        await pytest.correct_bulb.turn_on(PilotBuilder(rgb=(300, 0, 0)))
    # Green
    with pytest.raises(ValueError):
        await pytest.correct_bulb.turn_on(PilotBuilder(rgb=(0, 300, 0)))
    # Blue
    with pytest.raises(ValueError):
        await pytest.correct_bulb.turn_on(PilotBuilder(rgb=(0, 0, 300)))


@pytest.mark.asyncio
async def test_error_PilotBuilder_scene(data):
    """Error Screen."""
    with pytest.raises(ValueError):
        await pytest.correct_bulb.turn_on(PilotBuilder(scene=532))


# Error states / Timout
@pytest.mark.asyncio
async def test_timeout(data):
    """Test the timout exception after."""
    pytest.correct_bulb
    with pytest.raises(WizLightTimeOutError):
        await pytest.bad_bulb.getBulbConfig()


@pytest.mark.asyncio
async def test_timeout_PilotBuilder(data):
    """Test Timout for Result."""
    # check if the bulb state it given as bool - mock ?
    with pytest.raises(WizLightTimeOutError):
        await pytest.bad_bulb.turn_on(PilotBuilder(brightness=255))
