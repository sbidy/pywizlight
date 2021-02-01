"""Tests for the Bulb API."""
import pytest

from pywizlight import SCENES, PilotBuilder, wizlight
from pywizlight.exceptions import WizLightTimeOutError
from pywizlight.tests.fake_bulb import startup_bulb
from pywizlight.discovery import discover_lights


class TestBulb:
    """Bulb test class."""

    def pytest_namespace(self):
        """Define the global var."""
        return {"correct_bulb": wizlight, "bad_bulb": wizlight}

    @pytest.fixture
    def data(self):
        """Init the bad and good bulbs."""
        pytest.correct_bulb = wizlight(ip="127.0.0.1")
        pytest.bad_bulb = wizlight(ip="1.1.1.1")

    @classmethod
    def setup_class(cls):
        """Startup the class."""
        # Init the fake bulb on localhost
        startup_bulb(module_name="ESP01_SHRGB_03")

    # Non-Error states - PilotBuilder - Turn On
    @pytest.mark.asyncio
    async def test_Bulb_Discovery(self):
        """Test discovery function."""
        bulbs = await discover_lights(broadcast_space="192.168.178.255")
        for bulb in bulbs:
            state = await bulb.updateState()
            assert state.get_state() is False

    @pytest.mark.asyncio
    async def test_PilotBuilder_state(self, data):
        """Test State."""
        state = await pytest.correct_bulb.updateState()
        assert state.get_state() is False

    @pytest.mark.asyncio
    async def test_PilotBuilder_colortemp(self, data):
        """Test Color Temp."""
        await pytest.correct_bulb.turn_on(PilotBuilder(colortemp=2800))
        state = await pytest.correct_bulb.updateState()

        assert state.get_colortemp() == 2800

    @pytest.mark.asyncio
    async def test_PilotBuilder_brightness(self, data):
        """Test Brightness."""
        await pytest.correct_bulb.turn_on(PilotBuilder(brightness=10))
        state = await pytest.correct_bulb.updateState()
        # 10% == 26 in Hex
        assert state.get_brightness() == 26

    @pytest.mark.asyncio
    async def test_PilotBuilder_warm_wite(self, data):
        """Test Warm White."""
        await pytest.correct_bulb.turn_on(PilotBuilder(warm_white=255))
        state = await pytest.correct_bulb.updateState()

        assert state.get_warm_white() == 255

    @pytest.mark.asyncio
    async def test_PilotBuilder_cold_white(self, data):
        """Test Cold White."""
        await pytest.correct_bulb.turn_on(PilotBuilder(cold_white=255))
        state = await pytest.correct_bulb.updateState()

        assert state.get_cold_white() == 255

    @pytest.mark.asyncio
    async def test_PilotBuilder_rgb(self, data):
        """Test RGB Value."""
        await pytest.correct_bulb.turn_on(PilotBuilder(rgb=(0, 128, 255)))
        state = await pytest.correct_bulb.updateState()

        assert state.get_rgb() == (0, 128, 255)

    @pytest.mark.asyncio
    async def test_PilotBuilder_scene(self, data):
        """Test Screen."""
        await pytest.correct_bulb.turn_on(PilotBuilder(scene=1))
        state = await pytest.correct_bulb.updateState()

        assert state.get_scene() == SCENES[1]

    # ------ Error states -------------------------------------
    @pytest.mark.asyncio
    async def test_error_PilotBuilder_brightness(self, data):
        """Error Brightness."""
        with pytest.raises(ValueError):
            await pytest.correct_bulb.turn_on(PilotBuilder(brightness=500))

    @pytest.mark.asyncio
    async def test_error_PilotBuilder_warm_wite(self, data):
        """Error Warm White."""
        with pytest.raises(ValueError):
            await pytest.correct_bulb.turn_on(PilotBuilder(warm_white=300))
        with pytest.raises(ValueError):
            await pytest.correct_bulb.turn_on(PilotBuilder(warm_white=0))

    @pytest.mark.asyncio
    async def test_error_PilotBuilder_cold_white_upper(self, data):
        """Error Cold White."""
        with pytest.raises(ValueError):
            await pytest.correct_bulb.turn_on(PilotBuilder(cold_white=300))

    @pytest.mark.asyncio
    async def test_error_PilotBuilder_cold_white_lower(self, data):
        """Error Cold White."""
        with pytest.raises(ValueError):
            await pytest.correct_bulb.turn_on(PilotBuilder(cold_white=0))

    @pytest.mark.asyncio
    async def test_error_PilotBuilder_r(self, data):
        """Error Red Value."""
        with pytest.raises(ValueError):
            await pytest.correct_bulb.turn_on(PilotBuilder(rgb=(300, 0, 0)))

    @pytest.mark.asyncio
    async def test_error_PilotBuilder_green(self, data):
        """Error Green Value."""
        with pytest.raises(ValueError):
            await pytest.correct_bulb.turn_on(PilotBuilder(rgb=(0, 300, 0)))

    @pytest.mark.asyncio
    async def test_error_PilotBuilder_blue(self, data):
        """Error Blue Value."""
        with pytest.raises(ValueError):
            await pytest.correct_bulb.turn_on(PilotBuilder(rgb=(0, 0, 300)))

    @pytest.mark.asyncio
    async def test_error_PilotBuilder_scene(self, data):
        """Error Screen."""
        with pytest.raises(ValueError):
            await pytest.correct_bulb.turn_on(PilotBuilder(scene=532))

    # Error states / Timout
    @pytest.mark.asyncio
    async def test_timeout(self, data):
        """Test the timout exception after."""
        pytest.correct_bulb
        with pytest.raises(WizLightTimeOutError):
            await pytest.bad_bulb.getBulbConfig()

    @pytest.mark.asyncio
    async def test_timeout_PilotBuilder(self, data):
        """Test Timout for Result."""
        # check if the bulb state it given as bool - mock ?
        with pytest.raises(WizLightTimeOutError):
            await pytest.bad_bulb.turn_on(PilotBuilder(brightness=255))
