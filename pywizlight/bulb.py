"""pywizlight integration."""
import asyncio
import contextlib
import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

from pywizlight.exceptions import WizLightNotKnownBulb

from pywizlight.bulblibrary import BulbType
from pywizlight.exceptions import (
    WizLightConnectionError,
    WizLightMethodNotFound,
    WizLightTimeOutError,
)
from pywizlight.models import DiscoveredBulb
from pywizlight.protocol import WizProtocol
from pywizlight.push_manager import PushManager
from pywizlight.rgbcw import hs2rgbcw, rgb2rgbcw
from pywizlight.scenes import SCENES, SCENES_BY_CLASS
from pywizlight.utils import hex_to_percent, percent_to_hex, to_wiz_json
from pywizlight.vec import Vector

_LOGGER = logging.getLogger(__name__)


BulbResponse = Dict[str, Any]


PORT = 38899

# Progressive backoff config
# ===============================================================
# We send datagrams at 0, 0.75, 2.25, 5.25, 8.25, 11.25
# We wait up to 11s for the last response before declaring failure
# ================================================================
TIMEOUT = 13  # How long we will wait total
MAX_SEND_DATAGRAMS = 6  # The maximum datagrams we send
FIRST_SEND_INTERVAL = 0.75  # This is the first wait time
MAX_BACKOFF = 3  # This is how far we will backoff

PUSH_KEEP_ALIVE_INTERVAL = 20
MAX_TIME_BETWEEN_PUSH = PUSH_KEEP_ALIVE_INTERVAL + TIMEOUT


NEVER_TIME = -120.0


RGB_ORDER = ["r", "g", "b"]
RGB_COLORS = set(RGB_ORDER)
RGBW_ORDER = ["r", "g", "b", "w"]
RGBW_COLORS = set(RGBW_ORDER)
RGBWW_ORDER = ["r", "g", "b", "c", "w"]
RGBWW_COLORS = set(RGBWW_ORDER)

_IGNORE_STATE_KEYS = {"mqttCd", "ts", "rssi"}
PIR_SOURCE = "pir"

WIZMOTE_BUTTON_MAP = {
    "wfa1": "on",
    "wfa2": "off",
    "wfa3": "night",
    "wfa8": "decrease_brightness",
    "wfa9": "increase_brightness",
    "wfa16": "1",
    "wfa17": "2",
    "wfa18": "3",
    "wfa19": "4",
}

ALWAYS_SEND_SRCS = set([PIR_SOURCE, *WIZMOTE_BUTTON_MAP])


def states_match(old: Dict[str, Any], new: Dict[str, Any]) -> bool:
    """Check if states match except for keys we do not want to callback on."""
    old_src = old.get("src")
    new_src = new.get("src")
    # Always send the update when there is a PIR change or button press.
    if new_src != old_src and (
        new_src in ALWAYS_SEND_SRCS or old_src in ALWAYS_SEND_SRCS
    ):
        return False
    for key, val in new.items():
        if key != "src" and old.get(key) != val and key not in _IGNORE_STATE_KEYS:
            return False
    return True


def _rgb_in_range_or_raise(rgb: Tuple[Union[float, int], ...]) -> None:
    if not (0 <= rgb[0] < 256):
        raise ValueError("Red is not in range between 0-255.")
    if not (0 <= rgb[1] < 256):
        raise ValueError("Green is not in range between 0-255.")
    if not (0 <= rgb[2] < 256):
        raise ValueError("Blue is not in range between 0-255.")


def _validate_speed_or_raise(speed: int) -> None:
    if not 10 <= speed <= 200:
        raise ValueError("Value must be between 10 and 200")


class PilotBuilder:
    """Get information from the bulb."""

    def __init__(
        self,
        warm_white: Optional[int] = None,
        cold_white: Optional[int] = None,
        speed: Optional[int] = None,
        scene: Optional[int] = None,
        rgb: Optional[Tuple[float, float, float]] = None,
        rgbw: Optional[Tuple[int, int, int, int]] = None,
        rgbww: Optional[Tuple[int, int, int, int, int]] = None,
        hucolor: Optional[Tuple[float, float]] = None,
        brightness: Optional[int] = None,
        colortemp: Optional[int] = None,
        state: bool = True,
    ) -> None:
        """Set the parameter."""
        self.pilot_params: Dict[str, Any] = {"state": state}
        if speed is not None:
            self._set_speed(speed)
        if scene is not None:
            self._set_scene(scene)
        if brightness is not None:
            self._set_brightness(brightness)
        if rgb is not None:
            self._set_rgb(rgb)
        elif rgbw is not None:
            self._set_rgbw(rgbw)
        elif rgbww is not None:
            self._set_rgbww(rgbww)
        elif colortemp is not None:
            self._set_colortemp(colortemp)
        elif hucolor is not None:
            self._set_hs_color(hucolor)
        if warm_white is not None:
            self._set_warm_white(warm_white)
        if cold_white is not None:
            self._set_cold_white(cold_white)

    def set_pilot_message(self) -> str:
        """Return the pilot message."""
        return to_wiz_json({"method": "setPilot", "params": self.pilot_params})

    def set_state_message(self, state: bool) -> str:
        """Return the setState message. It doesn't change the current status of the light."""
        self.pilot_params["state"] = state
        return to_wiz_json({"method": "setState", "params": self.pilot_params})

    def _set_warm_white(self, value: int) -> None:
        """Set the value of the warm white led."""
        if not 0 <= value < 256:
            raise ValueError("Value must be between 0 and 255")
        self.pilot_params["w"] = value

    def _set_cold_white(self, value: int) -> None:
        """Set the value of the cold white led."""
        if not 0 <= value < 256:
            raise ValueError("Value must be between 0 and 255")
        self.pilot_params["c"] = value

    def _set_speed(self, value: int) -> None:
        """Set the effect changing speed (10-200)."""
        # This applies only to changing effects.
        _validate_speed_or_raise(value)
        self.pilot_params["speed"] = value

    def _set_scene(self, scene_id: int) -> None:
        """Set the scene by id."""
        if scene_id not in SCENES:
            # id not in SCENES !
            raise ValueError("Scene is not available. Only 0 to 32 are supported")
        self.pilot_params["sceneId"] = scene_id

    def _set_rgbw(self, rgbw: Tuple[int, int, int, int]) -> None:
        """Set the RGBW color state of the bulb."""
        _rgb_in_range_or_raise(rgbw)
        self.pilot_params.update({key: rgbw[idx] for idx, key in enumerate(RGB_ORDER)})
        self._set_warm_white(rgbw[3])

    def _set_rgbww(self, rgbww: Tuple[int, int, int, int, int]) -> None:
        """Set the RGBWW color state of the bulb."""
        _rgb_in_range_or_raise(rgbww)
        params = self.pilot_params
        params.update({key: rgbww[idx] for idx, key in enumerate(RGB_ORDER)})
        self._set_cold_white(rgbww[3])
        self._set_warm_white(rgbww[4])

    def _set_rgb(self, values: Tuple[float, float, float]) -> None:
        """Set the RGB color state of the bulb."""
        # Setup the tuples for the RGB values
        red, green, blue = values
        _rgb_in_range_or_raise(values)
        # Get the RGB+CW values
        rgb_out, cw = rgb2rgbcw(values)
        # Extract the RGB values
        params = self.pilot_params
        params.update({key: rgb_out[idx] for idx, key in enumerate(RGB_ORDER)})
        # No CW because of full RGB color
        if cw is not None:
            # Use the existing set_warm_white function to set the CW values
            self._set_warm_white(cw)

    def _set_hs_color(self, values: Tuple[float, float]) -> None:
        """Set the HS color state of the bulb."""
        # Transform the HS values to RGB+CW values
        rgb, cw = hs2rgbcw(values)
        _rgb_in_range_or_raise(rgb)
        # Set the RGB values
        params = self.pilot_params
        params.update({key: rgb[idx] for idx, key in enumerate(RGB_ORDER)})
        if cw is not None:
            # Use the existing set_warm_white function to set the CW values
            self._set_warm_white(cw)

    def _set_brightness(self, value: int) -> None:
        """Set the value of the brightness 0-255."""
        percent = hex_to_percent(value)
        if percent > 101:
            raise ValueError("Max value can be 100% with 255.")
        # hardware limitation - values less than 10% are not supported
        self.pilot_params["dimming"] = max(10, percent)

    def _set_colortemp(self, kelvin: int) -> None:
        """Set the color temperature for the white led in the bulb."""
        # normalize the kelvin values - should be removed
        self.pilot_params["temp"] = min(10000, max(1000, kelvin))


def _extract_bool(response: BulbResponse, key: str) -> Optional[bool]:
    return bool(response[key]) if key in response else None


def _extract_str(response: BulbResponse, key: str) -> Optional[str]:
    return str(response[key]) if key in response else None


def _extract_int(response: BulbResponse, key: str) -> Optional[int]:
    return int(response[key]) if key in response else None


class PilotParser:
    """Interpret the message from the bulb."""

    def __init__(self, pilotResult: BulbResponse) -> None:
        """Init the class."""
        self.pilotResult = pilotResult

    def get_state(self) -> Optional[bool]:
        """Return the state of the bulb."""
        return _extract_bool(self.pilotResult, "state")

    def get_source(self) -> Optional[str]:
        """Return the source of the state change."""
        return _extract_str(self.pilotResult, "src")

    def get_mac(self) -> Optional[str]:
        """Return MAC from the bulb."""
        return _extract_str(self.pilotResult, "mac")

    def get_warm_white(self) -> Optional[int]:
        """Get the value of the warm white led."""
        return _extract_int(self.pilotResult, "w")

    def get_white_range(self) -> Optional[List[float]]:
        """Get the value of the whiteRange property."""
        if "whiteRange" in self.pilotResult:
            return [float(x) for x in self.pilotResult["whiteRange"]]
        return None

    def get_extended_white_range(self) -> Optional[List[float]]:
        """Get the value of the extended whiteRange property."""
        if "extRange" in self.pilotResult:
            return [float(x) for x in self.pilotResult["extRange"]]
        # New after v1.22 FW - "cctRange":[2200,2700,6500,6500]
        elif "cctRange" in self.pilotResult:
            return [float(x) for x in self.pilotResult["cctRange"]]
        return None

    def get_speed(self) -> Optional[int]:
        """Get the color changing speed."""
        return _extract_int(self.pilotResult, "speed")

    def get_scene_id(self) -> Optional[int]:
        if "schdPsetId" in self.pilotResult:  # rhythm
            return 1000
        return self.pilotResult.get("sceneId")

    def get_scene(self) -> Optional[str]:
        """Get the current scene name."""
        scene_id = self.get_scene_id()
        if scene_id is None:
            return None
        return SCENES.get(scene_id)

    def get_cold_white(self) -> Optional[int]:
        """Get the value of the cold white led."""
        return _extract_int(self.pilotResult, "c")

    def get_rgb(self) -> Union[Tuple[None, None, None], Vector]:
        """Get the RGB color state of the bulb and turns it on."""
        state = self.pilotResult
        if RGB_COLORS.issubset(state):
            return tuple(int(state[val]) for val in RGB_ORDER)
        # no RGB color value was set
        return None, None, None

    def get_rgbw(self) -> Optional[Tuple[int, int, int, int]]:
        """Get the RGBW color of the device."""
        state = self.pilotResult
        if not RGBW_COLORS.issubset(state):
            return None
        return cast(
            Tuple[int, int, int, int], tuple(int(state[val]) for val in RGBW_ORDER)
        )

    def get_rgbww(self) -> Optional[Tuple[int, int, int, int, int]]:
        """Get the RGBWW color of the device."""
        state = self.pilotResult
        if not RGBWW_COLORS.issubset(state):
            return None
        return cast(
            Tuple[int, int, int, int, int],
            tuple(int(state[val]) for val in RGBWW_ORDER),
        )

    def get_brightness(self) -> Optional[int]:
        """Get the value of the brightness 0-255."""
        if "dimming" in self.pilotResult:
            return percent_to_hex(self.pilotResult["dimming"])
        return None

    def get_colortemp(self) -> Optional[int]:
        """Get the color temperature from the bulb."""
        return _extract_int(self.pilotResult, "temp")


async def _send_udp_message_with_retry(
    message: str,
    transport: asyncio.DatagramTransport,
    response_future: asyncio.Future,
    ip: str,
    port: int,
) -> None:
    """Send a UDP message multiple times until we reach the maximum or a response is recieved."""
    data = message.encode("utf-8")
    send_wait = FIRST_SEND_INTERVAL
    total_waited = 0.0
    for send in range(MAX_SEND_DATAGRAMS):
        if transport.is_closing() or response_future.done():
            return
        attempt = send + 1
        _LOGGER.debug(
            "%s: >> %s (%s/%s) backoff=%s",
            ip,
            data,
            attempt,
            MAX_SEND_DATAGRAMS,
            total_waited,
        )
        transport.sendto(data, (ip, port))
        await asyncio.sleep(send_wait)
        total_waited += send_wait
        send_wait = min(send_wait * 2, MAX_BACKOFF)


class wizlight:
    """Create an instance of a WiZ Light Bulb."""

    # default port for WiZ lights - 38899

    def __init__(
        self,
        ip: str,
        port: int = PORT,
        mac: Optional[str] = None,
    ) -> None:
        """Create instance with the IP address of the bulb."""
        self.ip = ip
        self.port = port
        self.state: Optional[PilotParser] = None
        self.mac = mac
        self.bulbtype: Optional[BulbType] = None
        self.modelConfig: Optional[Dict] = None
        self.whiteRange: Optional[List[float]] = None
        self.extwhiteRange: Optional[List[float]] = None
        self.transport: Optional[asyncio.DatagramTransport] = None
        self.protocol: Optional[WizProtocol] = None

        self.lock = asyncio.Lock()
        self.loop = asyncio.get_event_loop()
        self.push_callback: Optional[Callable[[PilotParser], None]] = None
        self.response_future: Optional[asyncio.Future] = None
        self.push_cancel: Optional[Callable] = None
        self.last_push: float = NEVER_TIME
        self.push_running: bool = False
        # Check connection removed as it did blocking I/O in the event loop

    @property
    def status(self) -> Optional[bool]:
        """Return the status of the bulb: true = on, false = off."""
        if self.state is None:
            return None
        return self.state.get_state()

    # ------------------ Non properties -------------- #

    async def _ensure_connection(self) -> None:
        """Ensure we are connected."""
        if self.transport:
            return
        transport_proto = await self.loop.create_datagram_endpoint(
            lambda: WizProtocol(on_response=self._on_response, on_error=self._on_error),
            remote_addr=(self.ip, self.port),
        )
        self.transport = cast(asyncio.DatagramTransport, transport_proto[0])
        self.protocol = cast(WizProtocol, transport_proto[1])

    def register(self) -> None:
        """Call register to keep alive push updates."""
        if self.push_running:
            push_manager = PushManager().get()
            asyncio.create_task(self._async_send_register(push_manager.register_msg))
            self.loop.call_later(PUSH_KEEP_ALIVE_INTERVAL, self.register)

    async def _async_send_register(self, message: str) -> None:
        """Send the registration message."""
        try:
            await self.sendUDPMessage(message)
        except (WizLightTimeOutError, WizLightConnectionError) as ex:
            _LOGGER.debug("%s: Registration for push updates failed: %s", self.ip, ex)

    async def start_push(
        self, callback: Optional[Callable[[PilotParser], None]]
    ) -> None:
        """Start periodic register calls to get push updates via syncPilot."""
        _LOGGER.debug("Enabling push updates for %s", self.mac)
        self.push_callback = callback
        push_manager = PushManager().get()
        self.push_cancel = push_manager.register(self.mac, self._on_push)
        if await push_manager.start(self.ip):
            self.push_running = True
            self.register()

    def set_discovery_callback(
        self, callback: Optional[Callable[[DiscoveredBulb], None]]
    ) -> None:
        """Set the callback for when a new device is discovered."""
        PushManager().get().set_discovery_callback(callback)

    def _on_push(self, resp: dict, addr: Tuple[str, int]) -> None:
        """Handle a syncPilot from the device."""
        self.last_push = time.monotonic()
        old_state = self.state.pilotResult if self.state else None
        new_state = resp["params"]
        if old_state and states_match(old_state, new_state):
            return
        self.state = PilotParser(new_state)
        if self.push_callback:
            self.push_callback(self.state)

    def _on_response(self, message: bytes, addr: Tuple[str, int]) -> None:
        """Handle a response from the device."""
        _LOGGER.debug("%s: << %s", self.ip, message)
        if self.response_future and not self.response_future.done():
            self.response_future.set_result(message)

    def _on_error(self, exception: Optional[Exception]) -> None:
        """Handle a protocol error."""
        if exception and self.response_future and not self.response_future.done():
            self.response_future.set_exception(exception)

    async def get_bulbtype(self) -> BulbType:
        """Return the bulb type as BulbType object."""
        if self.bulbtype is not None:
            return self.bulbtype

        bulb_config = await self.getBulbConfig()
        result = bulb_config["result"]
        if "moduleName" not in result:
            raise WizLightNotKnownBulb(
                "Unable to determine the bulb type; moduleName is missing from getSystemConfig"
            )
        white_range = await self.getExtendedWhiteRange()
        white_to_color_ratio = None
        white_channels = None
        if "drvConf" in result:
            # For old FW < 1.22
            white_to_color_ratio, white_channels = result["drvConf"]
        module_name = result["moduleName"]
        fw_version = result.get("fwVersion")
        model_result = self.modelConfig["result"] if self.modelConfig else {}
        white_channels = model_result.get("nowc", white_channels)
        white_to_color_ratio = model_result.get("wcr", white_to_color_ratio)
        self.bulbtype = BulbType.from_data(
            module_name, white_range, fw_version, white_channels, white_to_color_ratio
        )
        return self.bulbtype

    async def getWhiteRange(self) -> Optional[List[float]]:
        """Read the white range from the bulb."""
        if self.whiteRange is not None:
            return self.whiteRange

        resp = await self.getUserConfig()
        if resp is not None and "result" in resp:
            self.whiteRange = PilotParser(resp["result"]).get_white_range()

        return self.whiteRange

    async def getExtendedWhiteRange(self) -> Optional[List[float]]:
        """Read extended withe range from the RGB bulb."""
        if self.extwhiteRange is not None:
            return self.extwhiteRange

        # First for FW > 1.22
        resp = await self.getModelConfig()
        if resp is None or "result" not in resp:
            # For old FW < 1.22
            resp = await self.getUserConfig()

        if "result" in resp:
            self.extwhiteRange = PilotParser(resp["result"]).get_extended_white_range()

        return self.extwhiteRange

    async def getSupportedScenes(self) -> List[str]:
        """Return the supported scenes based on type.

        Lookup: https://docs.pro.wizconnected.com
        """
        if self.bulbtype is None:
            await self.get_bulbtype()
        assert self.bulbtype  # Should have gotten set by get_bulbtype
        return SCENES_BY_CLASS.get(self.bulbtype.bulb_type, [])

    async def turn_off(self) -> None:
        """Turn the light off."""
        await self.sendUDPMessage(r'{"method":"setPilot","params":{"state":false}}')

    async def reboot(self) -> None:
        """Reboot the bulb."""
        await self.sendUDPMessage(r'{"method":"reboot","params":{}}')

    async def reset(self) -> None:
        """Reset the bulb to factory defaults."""
        await self.sendUDPMessage(r'{"method":"reset","params":{}}')

    async def set_speed(self, speed: int) -> None:
        """Set the effect speed."""
        # If we have state: True in the setPilot, the speed does not change
        _validate_speed_or_raise(speed)
        await self.sendUDPMessage(
            to_wiz_json({"method": "setPilot", "params": {"speed": speed}})
        )

    async def turn_on(self, pilot_builder: PilotBuilder = PilotBuilder()) -> None:
        """Turn the light on with defined message.

        :param pilot_builder: PilotBuilder object to set the turn on state, defaults to PilotBuilder()
        :type pilot_builder: [type], optional
        """
        await self.sendUDPMessage(pilot_builder.set_pilot_message())

    async def set_state(self, pilot_builder: PilotBuilder = PilotBuilder()) -> None:
        """Set the state of the bulb with defined message. Doesn't turn on the light.

        :param pilot_builder: PilotBuilder object to set the state, defaults to PilotBuilder()
        :type pilot_builder: [type], optional
        """
        # TODO: self.status could be None, in which case casting it to a bool might not be what we really want
        await self.sendUDPMessage(pilot_builder.set_state_message(bool(self.status)))

    # ---------- Helper Functions ------------
    async def updateState(self) -> Optional[PilotParser]:
        """Update the bulb state.

        Note: Call this method before getting any other property.
        Also, call this method to update the current value for any property.
        getPilot - gets the current bulb state - no parameters need to be included
        {"method": "getPilot", "id": 24}
        """
        if self.last_push + MAX_TIME_BETWEEN_PUSH < time.monotonic():
            resp = await self.sendUDPMessage(r'{"method":"getPilot","params":{}}')
            if resp is not None and "result" in resp:
                self.state = PilotParser(resp["result"])
            else:
                self.state = None
        return self.state

    def _cache_mac_from_bulb_config(self, resp: BulbResponse) -> None:
        """Cache the mac when we fetch bulb config to avoid fetching it again."""
        if resp is not None and "result" in resp and self.mac is None:
            self.mac = PilotParser(resp["result"]).get_mac()

    async def getMac(self) -> Optional[str]:
        """Read the MAC from the bulb."""
        if not self.mac:
            await self.getBulbConfig()
        return self.mac

    async def getBulbConfig(self) -> BulbResponse:
        """Return the configuration from the bulb."""
        resp = await self.sendUDPMessage(r'{"method":"getSystemConfig","params":{}}')
        self._cache_mac_from_bulb_config(resp)
        return resp

    async def getModelConfig(self) -> Optional[BulbResponse]:
        """Return the new model capabilities from the bulb.
        Only available in bulb FW >1.22!
        """
        if self.modelConfig is None:
            with contextlib.suppress(WizLightMethodNotFound):
                self.modelConfig = await self.sendUDPMessage(
                    r'{"method":"getModelConfig","params":{}}'
                )
        return self.modelConfig

    async def getUserConfig(self) -> BulbResponse:
        """Return the user configuration from the bulb."""
        return await self.sendUDPMessage(r'{"method":"getUserConfig","params":{}}')

    async def lightSwitch(self) -> None:
        """Turn the light bulb on or off like a switch."""
        # first get the status
        state = await self.updateState()
        if not state:  # Did not get state, nothing to do
            return
        if state.get_state():
            # if the light is on - switch off
            await self.turn_off()
        else:
            # if the light is off - turn on
            await self.turn_on()

    async def sendUDPMessage(self, message: str) -> BulbResponse:
        """Send the UDP message to the bulb."""
        await self._ensure_connection()
        assert self.transport is not None
        async with self.lock:
            self.response_future = asyncio.Future()
            send_task = asyncio.create_task(
                _send_udp_message_with_retry(
                    message, self.transport, self.response_future, self.ip, self.port
                )
            )
            try:
                response = await asyncio.wait_for(
                    asyncio.shield(self.response_future), timeout=TIMEOUT
                )
            except OSError as ex:
                raise WizLightConnectionError(str(ex)) from ex
            except asyncio.TimeoutError:
                _LOGGER.debug(
                    "%s: Timed out waiting for response to %s after %s tries.",
                    self.ip,
                    message,
                    MAX_SEND_DATAGRAMS,
                )
                raise WizLightTimeOutError("The request to the bulb timed out")
            finally:
                await asyncio.sleep(0)  # Try to let the task finish without cancelation
                if not send_task.done():
                    send_task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await send_task
        resp = json.loads(response.decode())
        if "error" in resp:
            if resp["error"]["code"] == -32601:
                raise WizLightMethodNotFound("Method not found; maybe older bulb FW?")
            raise WizLightConnectionError(f'Error recieved: {resp["error"]}')
        return resp

    async def async_close(self):
        """Close the transport."""
        self._async_close()

    def _async_close(self):
        self.push_running = False
        if self.transport:
            self.transport.close()
            self.transport = None
        if self.push_cancel:
            self.push_cancel()
            self.push_cancel = None

    def __del__(self):
        """Close the connection when the object is destroyed."""
        if self.transport and not self.transport.is_closing():
            self.loop.call_soon_threadsafe(self._async_close)
