"""Tests for the Bulb API."""
from typing import AsyncGenerator
from unittest.mock import patch

import pytest

from pywizlight import SCENES, PilotBuilder, wizlight
from pywizlight.bulb import states_match
from pywizlight.bulblibrary import BulbClass, BulbType, Features, KelvinRange
from pywizlight.discovery import discover_lights
from pywizlight.exceptions import WizLightTimeOutError
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture()
async def correct_bulb() -> AsyncGenerator[wizlight, None]:
    shutdown, port = await startup_bulb(
        module_name="ESP01_SHRGB_03", firmware_version="1.25.0"
    )
    bulb = wizlight(ip="127.0.0.1", port=port)
    yield bulb
    await bulb.async_close()
    shutdown()


@pytest.fixture()
async def bad_bulb() -> AsyncGenerator[wizlight, None]:
    bulb = wizlight(ip="1.1.1.1")
    yield bulb
    await bulb.async_close()


# Non-Error states - PilotBuilder - Turn On
@pytest.mark.asyncio
async def test_Bulb_Discovery(correct_bulb: wizlight) -> None:
    """Test discovery function."""
    # Use a random available port since otherwise the
    # test may fail
    with patch("pywizlight.discovery.PORT", 0):
        bulbs = await discover_lights(broadcast_space="192.168.178.255", wait_time=0.02)
    for bulb in bulbs:
        with patch("pywizlight.bulb.FIRST_SEND_INTERVAL", 0.01), patch(
            "pywizlight.bulb.TIMEOUT", 0.01
        ):
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
async def test_PilotBuilder_hucolor(correct_bulb: wizlight) -> None:
    """Test RGB Value via hucolor."""
    await correct_bulb.turn_on(PilotBuilder(hucolor=(100, 50)))
    state = await correct_bulb.updateState()

    assert state and state.get_rgb() == (88.0, 255.0, 0.0)


@pytest.mark.asyncio
async def test_setting_rgbw(correct_bulb: wizlight) -> None:
    """Test setting rgbw."""
    await correct_bulb.turn_on(PilotBuilder(rgbw=(1, 2, 3, 4)))
    state = await correct_bulb.updateState()
    assert state and state.get_rgbw() == (1, 2, 3, 4)


@pytest.mark.asyncio
async def test_PilotBuilder_scene(correct_bulb: wizlight) -> None:
    """Test scene."""
    await correct_bulb.turn_on(PilotBuilder(scene=1))
    state = await correct_bulb.updateState()

    assert state and state.get_scene() == SCENES[1]
    state.pilotResult["schdPsetId"] = True
    assert state.get_scene() == SCENES[1000]


@pytest.mark.asyncio
async def test_PilotBuilder_scene_empty(correct_bulb: wizlight) -> None:
    """Test scene with no scene set."""
    state = await correct_bulb.updateState()
    assert state is not None
    if "sceneId" in state.pilotResult:
        del state.pilotResult["sceneId"]
    assert state and state.get_scene() is None


@pytest.mark.asyncio
async def test_PilotBuilder_speed(correct_bulb: wizlight) -> None:
    """Test speed."""
    await correct_bulb.turn_on(PilotBuilder(scene=1, speed=50))
    state = await correct_bulb.updateState()

    assert state and state.get_scene() == SCENES[1]
    assert state and state.get_speed() == 50


@pytest.mark.asyncio
async def test_set_speed(correct_bulb: wizlight) -> None:
    """Set speed."""
    await correct_bulb.set_speed(125)
    state = await correct_bulb.updateState()
    assert state and state.get_speed() == 125


@pytest.mark.asyncio
async def test_get_source(correct_bulb: wizlight) -> None:
    """Test getting the source."""
    state = await correct_bulb.updateState()
    assert state and state.get_source() == "udp"


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
async def test_error_PilotBuilder_cold_white(correct_bulb: wizlight) -> None:
    """Error Cold White Value."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(cold_white=9999))


@pytest.mark.asyncio
async def test_error_PilotBuilder_scene(correct_bulb: wizlight) -> None:
    """Error scene."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(scene=532))


@pytest.mark.asyncio
async def test_error_PilotBuilder_speed(correct_bulb: wizlight) -> None:
    """Error speed."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(speed=532))


@pytest.mark.asyncio
async def test_error_set_speed(correct_bulb: wizlight) -> None:
    """Error speed."""
    with pytest.raises(ValueError):
        await correct_bulb.set_speed(532)


@pytest.mark.asyncio
async def test_fw_version(correct_bulb: wizlight) -> None:
    """Test fetching the firmware version."""
    bulb_type = await correct_bulb.get_bulbtype()
    assert bulb_type == BulbType(
        features=Features(color=True, color_tmp=True, effect=True, brightness=True),
        name="ESP01_SHRGB_03",
        kelvin_range=KelvinRange(max=6500, min=2200),
        bulb_type=BulbClass.RGB,
        fw_version="1.25.0",
        white_channels=1,
        white_to_color_ratio=30,
    )
    assert correct_bulb.mac == "a8bb5006033d"


@pytest.mark.asyncio
async def test_get_mac(correct_bulb: wizlight) -> None:
    """Test getting the mac address."""
    mac = await correct_bulb.getMac()
    assert mac == "a8bb5006033d"
    mac = await correct_bulb.getMac()
    assert mac == "a8bb5006033d"


# Error states / Timout
@pytest.mark.asyncio
async def test_timeout(bad_bulb: wizlight) -> None:
    """Test the timout exception after."""
    with pytest.raises(WizLightTimeOutError), patch(
        "pywizlight.bulb.FIRST_SEND_INTERVAL", 0.01
    ), patch("pywizlight.bulb.TIMEOUT", 0.01):
        await bad_bulb.getBulbConfig()


@pytest.mark.asyncio
async def test_timeout_PilotBuilder(bad_bulb: wizlight) -> None:
    """Test Timout for Result."""
    # check if the bulb state it given as bool - mock ?
    with pytest.raises(WizLightTimeOutError), patch(
        "pywizlight.bulb.FIRST_SEND_INTERVAL", 0.01
    ), patch("pywizlight.bulb.TIMEOUT", 0.01):
        await bad_bulb.turn_on(PilotBuilder(brightness=255))


@pytest.mark.asyncio
async def test_states_match_with_occupancy() -> None:
    """Test states match always sends pir updates but we ignore mqttCd, rssi, and ts."""
    state_off_ios = {
        "mac": "a8bb50d46a1c",
        "rssi": -70,
        "src": "ios",
        "mqttCd": 0,
        "ts": 1644440635,
        "state": False,
        "sceneId": 0,
    }
    state_on_ios = {
        "mac": "a8bb50d46a1c",
        "rssi": -45,
        "src": "ios",
        "mqttCd": 0,
        "ts": 1644440662,
        "state": False,
        "sceneId": 27,
        "speed": 100,
        "dimming": 100,
    }
    state_on_hb = {
        "mac": "a8bb50d46a1c",
        "rssi": -45,
        "src": "hb",
        "mqttCd": 0,
        "ts": 1644440642,
        "state": False,
        "sceneId": 27,
        "speed": 100,
        "dimming": 100,
    }
    ios_scene27 = {
        "mac": "a8bb50d46a1c",
        "rssi": -48,
        "src": "ios",
        "state": True,
        "sceneId": 27,
        "speed": 100,
        "dimming": 100,
    }
    ios_off = {
        "mac": "a8bb50d46a1c",
        "rssi": -69,
        "src": "ios",
        "state": False,
        "sceneId": 0,
    }
    occupancy_detected_scene27 = {
        "mac": "a8bb50d46a1c",
        "rssi": -48,
        "src": "pir",
        "state": True,
        "sceneId": 27,
        "speed": 100,
        "dimming": 100,
    }
    occupancy_not_detected = {
        "mac": "a8bb50d46a1c",
        "rssi": -69,
        "src": "pir",
        "state": False,
        "sceneId": 0,
    }

    assert states_match(state_off_ios, state_off_ios)
    assert not states_match(state_off_ios, state_on_ios)
    assert states_match(
        state_on_ios, state_on_hb
    )  # source change does not matter unless its a PIR
    assert not states_match(
        ios_scene27, occupancy_detected_scene27
    )  # source change matters since its a PIR
    assert states_match(occupancy_detected_scene27, occupancy_detected_scene27)
    assert not states_match(
        ios_off, occupancy_not_detected
    )  # source change matters since its a PIR


@pytest.mark.asyncio
async def test_states_match_with_button() -> None:
    """Test states match always sends button updates but we ignore mqttCd, rssi, and ts."""

    button_on_press = {
        "mac": "a8bb50d46a1c",
        "rssi": -48,
        "src": "wfa1",
        "state": True,
    }
    button_off_press = {
        "mac": "a8bb50d46a1c",
        "rssi": -69,
        "src": "wfa2",
        "state": False,
        "sceneId": 0,
    }
    button_1_press_state_false = {
        "mac": "a8bb50d46a1c",
        "rssi": -69,
        "src": "wfa16",
        "state": False,
        "sceneId": 0,
    }
    button_1_press_state_true = {
        "mac": "a8bb50d46a1c",
        "rssi": -69,
        "src": "wfa16",
        "state": True,
        "sceneId": 0,
    }
    ios_off = {
        "mac": "a8bb50d46a1c",
        "rssi": -69,
        "src": "ios",
        "state": False,
        "sceneId": 0,
    }
    assert not states_match(button_on_press, button_off_press)
    assert not states_match(button_1_press_state_false, button_1_press_state_true)
    assert not states_match(
        ios_off, button_1_press_state_false
    )  # source change matters since its a button
