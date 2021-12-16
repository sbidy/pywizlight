"""pywizlight integration."""
import asyncio
import json
import logging
import socket
from time import time
from typing import Any, Dict, Tuple, Optional, Union, List

from asyncio_dgram.aio import connect as connect_dgram, DatagramStream

from pywizlight.bulblibrary import BulbClass, BulbType
from pywizlight.exceptions import (
    WizLightConnectionError,
    WizLightMethodNotFound,
    WizLightTimeOutError,
)
from pywizlight.rgbcw import hs2rgbcw, rgb2rgbcw
from pywizlight.scenes import SCENES
from pywizlight.utils import hex_to_percent, percent_to_hex
from pywizlight.vec import Vector

_LOGGER = logging.getLogger(__name__)
TW_SCENES = [6, 9, 10, 11, 12, 13, 14, 15, 16, 18, 29, 30, 31, 32]
DW_SCENES = [9, 10, 13, 14, 29, 30, 31, 32]

BulbResponse = Dict[str, Any]


class PilotBuilder:
    """Get information from the bulb."""

    def __init__(
        self,
        warm_white: Optional[int] = None,
        cold_white: Optional[int] = None,
        speed: Optional[int] = None,
        scene: Optional[int] = None,
        rgb: Optional[Tuple[float, float, float]] = None,
        hucolor: Optional[Tuple[float, float]] = None,
        brightness: Optional[int] = None,
        colortemp: Optional[int] = None,
        state: bool = True,
    ) -> None:
        """Set the parameter."""
        self.pilot_params: Dict[str, Any] = {"state": state}

        if warm_white is not None:
            self._set_warm_white(warm_white)
        if cold_white is not None:
            self._set_cold_white(cold_white)
        if speed is not None:
            self._set_speed(speed)
        if scene is not None:
            self._set_scene(scene)
        if rgb is not None:
            self._set_rgb(rgb)
        if brightness is not None:
            self._set_brightness(brightness)
        if colortemp is not None:
            self._set_colortemp(colortemp)
        if hucolor is not None:
            self._set_hs_color(hucolor)

    def set_pilot_message(self) -> str:
        """Return the pilot message."""
        return json.dumps({"method": "setPilot", "params": self.pilot_params})

    def set_state_message(self, state: bool) -> str:
        """Return the setState message. It doesn't change the current status of the light."""
        self.pilot_params["state"] = state
        return json.dumps({"method": "setState", "params": self.pilot_params})

    def _set_warm_white(self, value: int) -> None:
        """Set the value of the warm white led."""
        if 0 <= value < 256:
            self.pilot_params["w"] = value
        else:
            raise ValueError("Value must be between 0 and 255")

    def _set_cold_white(self, value: int) -> None:
        """Set the value of the cold white led."""
        if 0 <= value < 256:
            self.pilot_params["c"] = value
        else:
            raise ValueError("Value must be between 0 and 255")

    def _set_speed(self, value: int) -> None:
        """Set the color changing speed in precent (0-100)."""
        # This applies only to changing effects.
        if 0 < value < 101:
            self.pilot_params["speed"] = value
        else:
            raise ValueError("Value must be between 0 and 100")

    def _set_scene(self, scene_id: int) -> None:
        """Set the scene by id."""
        if scene_id in SCENES:
            self.pilot_params["sceneId"] = scene_id
        else:
            # id not in SCENES !
            raise ValueError("Scene is not available. Only 0 to 32 are supported")

    def _set_rgb(self, values: Tuple[float, float, float]) -> None:
        """Set the RGB color state of the bulb."""

        # Setup the tuples for the RGB values
        red, green, blue = values
        if 0 <= red < 256:
            self.pilot_params["r"] = red
        else:
            raise ValueError("Red is not in range between 0-255.")
        if 0 <= green < 256:
            self.pilot_params["g"] = green
        else:
            raise ValueError("Green is not in range between 0-255.")
        if 0 <= blue < 256:
            self.pilot_params["b"] = blue
        else:
            raise ValueError("Blue is not in range between 0-255.")
        # Get CW from RAW
        rgb_out, cw = rgb2rgbcw(values)
        # No CW because of full RGB color
        if cw is not None:
            # Use the existing set_warm_white function to set the CW values
            self._set_warm_white(cw)
            # Use the existing set_cold_white function to set the CW values
            self._set_cold_white(cw)

    def _set_hs_color(self, values: Tuple[float, float]) -> None:
        """Set the HS color state of the bulb."""
        # Transform the HS values to RGB+CW values
        rgb, cw = hs2rgbcw(values)
        red, green, blue = rgb
        if 0 <= red < 256:
            self.pilot_params["r"] = red
        else:
            raise ValueError("Red is not in range between 0-255.")
        if 0 <= green < 256:
            self.pilot_params["g"] = green
        else:
            raise ValueError("Green is not in range between 0-255.")
        if 0 <= blue < 256:
            self.pilot_params["b"] = blue
        else:
            raise ValueError("Blue is not in range between 0-255.")
        if cw is not None:
            # Use the existing set_warm_white function to set the CW values
            self._set_warm_white(cw)
            # Use the existing set_cold_white function to set the CW values
            self._set_cold_white(cw)

    def _set_brightness(self, value: int) -> None:
        """Set the value of the brightness 0-255."""
        percent = hex_to_percent(value)
        # hardware limitation - values less than 10% are not supported
        if percent < 10:
            percent = 10
        if percent > 101:
            raise ValueError("Max value can be 100% with 255.")
        self.pilot_params["dimming"] = percent

    def _set_colortemp(self, kelvin: int) -> None:
        """Set the color temperature for the white led in the bulb."""
        # normalize the kelvin values - should be removed
        if kelvin < 1000:
            kelvin = 1000
        if kelvin > 10000:
            kelvin = 10000

        self.pilot_params["temp"] = kelvin


class PilotParser:
    """Interpret the message from the bulb."""

    def __init__(self, pilotResult: BulbResponse) -> None:
        """Init the class."""
        self.pilotResult = pilotResult

    def get_state(self) -> Optional[bool]:
        """Return the state of the bulb."""
        if "state" in self.pilotResult:
            return bool(self.pilotResult["state"])
        else:
            return None

    def get_mac(self) -> Optional[str]:
        """Return MAC from the bulb."""
        if "mac" in self.pilotResult:
            return str(self.pilotResult["mac"])
        else:
            return None

    def get_warm_white(self) -> Optional[int]:
        """Get the value of the warm white led."""
        if "w" in self.pilotResult:
            return int(self.pilotResult["w"])
        else:
            return None

    def get_white_range(self) -> Optional[List[float]]:
        """Get the value of the whiteRange property."""
        if "whiteRange" in self.pilotResult:
            return [float(x) for x in self.pilotResult["whiteRange"]]
        else:
            return None

    def get_extended_white_range(self) -> Optional[List[float]]:
        """Get the value of the extended whiteRange property."""
        if "extRange" in self.pilotResult:
            return [float(x) for x in self.pilotResult["extRange"]]
        # New after v1.22 FW - "cctRange":[2200,2700,6500,6500]
        elif "cctRange" in self.pilotResult:
            return [float(x) for x in self.pilotResult["cctRange"]]
        else:
            return None

    def get_speed(self) -> Optional[int]:
        """Get the color changing speed."""
        if "speed" in self.pilotResult:
            return int(self.pilotResult["speed"])
        else:
            return None

    def get_scene(self) -> Optional[str]:
        """Get the current scene name."""
        if "schdPsetId" in self.pilotResult:  # rhythm
            return SCENES[1000]

        scene_id = self.pilotResult["sceneId"]
        if scene_id in SCENES:
            return SCENES[scene_id]
        else:
            return None

    def get_cold_white(self) -> Optional[int]:
        """Get the value of the cold white led."""
        if "c" in self.pilotResult:
            return int(self.pilotResult["c"])
        else:
            return None

    def get_rgb(self) -> Union[Tuple[None, None, None], Vector]:
        """Get the RGB color state of the bulb and turns it on."""
        if (
            "r" in self.pilotResult
            and "g" in self.pilotResult
            and "b" in self.pilotResult
        ):
            r = self.pilotResult["r"]
            g = self.pilotResult["g"]
            b = self.pilotResult["b"]
            return float(r), float(g), float(b)
        else:
            # no RGB color value was set
            return None, None, None

    def get_brightness(self) -> Optional[int]:
        """Get the value of the brightness 0-255."""
        if "dimming" in self.pilotResult:
            return percent_to_hex(self.pilotResult["dimming"])
        return None

    def get_colortemp(self) -> Optional[int]:
        """Get the color temperature from the bulb."""
        if "temp" in self.pilotResult:
            return int(self.pilotResult["temp"])
        else:
            return None


async def receiveUDPwithTimeout(stream: DatagramStream, timeout: float) -> bytes:
    """Get message with timeout value."""
    data, remote_addr = await asyncio.wait_for(stream.recv(), timeout)
    return data


class wizlight:
    """Create an instance of a WiZ Light Bulb."""

    # default port for WiZ lights - 38899

    def __init__(
        self,
        ip: str,
        connect_on_init: bool = False,
        port: int = 38899,
        mac: Optional[str] = None,
    ) -> None:
        """Create instance with the IP address of the bulb."""
        self.ip = ip
        self.port = port
        self.state: Optional[PilotParser] = None
        self.mac = mac
        self.bulbtype: Optional[BulbType] = None
        self.whiteRange: Optional[List[float]] = None
        self.extwhiteRange: Optional[List[float]] = None
        # check the state on init
        if connect_on_init:
            self._check_connection()

    @property
    def status(self) -> Optional[bool]:
        """Return the status of the bulb: true = on, false = off."""
        if self.state is None:
            return None
        return self.state.get_state()

    # ------------------ Non properties -------------- #

    def _check_connection(self) -> None:
        """Check the connection to the bulb."""
        message = r'{"method":"getPilot","params":{}}'
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        try:
            # send a udp package
            sock.sendto(bytes(message, "utf-8"), (self.ip, self.port))
            # get response data
            data, addr = sock.recvfrom(1024)
            if data:
                return
        except socket.timeout:
            raise WizLightTimeOutError(
                "No connection was established by initialization."
            )

    async def get_bulbtype(self) -> BulbType:
        """Return the bulb type as BulbType object."""
        if self.bulbtype is not None:
            return self.bulbtype

        bulb_config = await self.getBulbConfig()
        if "moduleName" not in bulb_config["result"]:
            raise ValueError("Unable to determine bulb type.")
        white_range = await self.getExtendedWhiteRange()
        module_name = bulb_config["result"]["moduleName"]
        self.bulbtype = BulbType.from_data(module_name, white_range)
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
        if resp is not None and "result" in resp:
            self.extwhiteRange = PilotParser(resp["result"]).get_extended_white_range()
        else:
            # For old FW < 1.22
            resp = await self.getUserConfig()
            if "result" in resp:
                self.extwhiteRange = PilotParser(
                    resp["result"]
                ).get_extended_white_range()
        return self.extwhiteRange

    async def getSupportedScenes(self) -> List[str]:
        """Return the supported scenes based on type.

        Lookup: https://docs.pro.wizconnected.com
        """
        if self.bulbtype is None:
            await self.get_bulbtype()
        assert self.bulbtype  # Should have gotten set by get_bulbtype
        # return for TW
        if self.bulbtype.bulb_type == BulbClass.TW:
            return [SCENES[key] for key in TW_SCENES]
        # retrun for DW
        if self.bulbtype.bulb_type == BulbClass.DW:
            return [SCENES[key] for key in DW_SCENES]
        # return for RGB - all scenes supported
        return list(SCENES.values())

    async def turn_off(self) -> None:
        """Turn the light off."""
        message = r'{"method":"setPilot","params":{"state":false}}'
        await self.sendUDPMessage(message)

    async def reboot(self) -> None:
        """Reboot the bulb."""
        message = r'{"method":"reboot","params":{}}'
        await self.sendUDPMessage(message)

    async def reset(self) -> None:
        """Reset the bulb to factory defaults."""
        message = r'{"method":"reset","params":{}}'
        await self.sendUDPMessage(message)

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
        message = r'{"method":"getPilot","params":{}}'
        resp = await self.sendUDPMessage(message)
        if resp is not None and "result" in resp:
            self.state = PilotParser(resp["result"])
        else:
            self.state = None
        return self.state

    async def getMac(self) -> Optional[str]:
        """Read the MAC from the bulb."""
        resp = await self.getBulbConfig()
        if resp is not None and "result" in resp and self.mac is None:
            self.mac = PilotParser(resp["result"]).get_mac()
        else:
            self.mac = None
        return self.mac

    async def getBulbConfig(self) -> BulbResponse:
        """Return the configuration from the bulb."""
        message = r'{"method":"getSystemConfig","params":{}}'
        return await self.sendUDPMessage(message)

    async def getModelConfig(self) -> Optional[BulbResponse]:
        """Return the new model capabilities from the bulb.
        Only available in bulb FW >1.22!
        """
        try:
            message = r'{"method":"getModelConfig","params":{}}'
            return await self.sendUDPMessage(message)
        except WizLightMethodNotFound:
            return None

    async def getUserConfig(self) -> BulbResponse:
        """Return the user configuration from the bulb."""
        message = r'{"method":"getUserConfig","params":{}}'
        return await self.sendUDPMessage(message)

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
        connid = hex(int(time() * 10000000))[2:]
        # overall 10 sec. for timeout
        timeout = 10
        send_interval = 0.5
        max_send_datagrams = int(timeout / send_interval)

        stream = None

        try:
            _LOGGER.debug(
                f"[wizlight {self.ip}, connid {connid}] connecting to UDP port "
                f"with send_interval of {send_interval} sec.."
            )
            stream = await asyncio.wait_for(
                connect_dgram((self.ip, self.port)), timeout
            )
            _LOGGER.debug(
                f"[wizlight {self.ip}, connid {connid}] listening for response datagram"
            )

            receive_task = asyncio.create_task(receiveUDPwithTimeout(stream, timeout))

            for i in range(max_send_datagrams):
                _LOGGER.debug(
                    f"[wizlight {self.ip}, connid {connid}] sending command datagram {i}: {message}"
                )
                asyncio.create_task(stream.send(bytes(message, "utf-8")))
                done, pending = await asyncio.wait(
                    [receive_task], timeout=send_interval
                )
                if done:
                    break

            await receive_task
            data = receive_task.result()

        except asyncio.TimeoutError:
            _LOGGER.debug(
                f"[wizlight {self.ip}, connid {connid}] Failed to do UDP call(s) to wiz light - Timeout Error!",
                exc_info=False,
            )
            raise WizLightTimeOutError("The request to the bulb timed out")
        finally:
            if stream:
                stream.close()
            else:
                raise WizLightConnectionError(
                    "Bulb is offline or IP address is not correct."
                )
        if data is not None and len(data) is not None:
            resp = dict(json.loads(data.decode()))
            if "error" not in resp:
                _LOGGER.debug(
                    f"[wizlight {self.ip}, connid {connid}] response received: {resp}"
                )
                return resp
            elif resp["error"]["code"] == -32601:
                raise WizLightMethodNotFound(
                    "Cant found the methode. Maybe older bulb FW?"
                )
        # exception should be created
        raise ValueError(f"Can't read response from the bulb. Debug: {data!r}")
