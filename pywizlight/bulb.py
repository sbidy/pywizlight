"""pywizlight integration."""
import asyncio
import json
import logging
import socket
from time import time

import asyncio_dgram

from pywizlight.bulblibrary import BulbType, Features, KelvinRange, BulbClass
from pywizlight.exceptions import (
    WizLightConnectionError,
    WizLightNotKnownBulb,
    WizLightTimeOutError,
    WizLightMethodeNotFound,
)
from pywizlight.scenes import SCENES

_LOGGER = logging.getLogger(__name__)


class PilotBuilder:
    """Get information from the bulb."""

    def __init__(
        self,
        warm_white=None,
        cold_white=None,
        speed=None,
        scene=None,
        rgb=None,
        brightness=None,
        colortemp=None,
        state=True,
    ):
        """Set the parameter."""
        if state:
            self.pilot_params = {"state": state}
        else:
            self.pilot_params = {"state": state}

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

    def set_pilot_message(self):
        """Return the pilot message."""
        return json.dumps({"method": "setPilot", "params": self.pilot_params})

    def set_state_message(self, state):
        """Return the setState message. It doesn't change the current status of the light."""
        self.pilot_params["state"] = state
        return json.dumps({"method": "setState", "params": self.pilot_params})

    def _set_warm_white(self, value: int):
        """Set the value of the cold white led."""
        if value > 0 and value < 256:
            self.pilot_params["w"] = value
        else:
            raise ValueError("Value must be between 1 and 255")

    def _set_cold_white(self, value: int):
        """Set the value of the cold white led."""
        if value > 0 and value < 256:
            self.pilot_params["c"] = value
        else:
            raise ValueError("Value must be between 1 and 255")

    def _set_speed(self, value: int):
        """Set the color changing speed in precent (0-100).

        This applies only to changing effects.
        """
        if value > 0 and value < 101:
            self.pilot_params["speed"] = value
        else:
            raise ValueError("Value must be between 0 and 100")

    def _set_scene(self, scene_id: int):
        """Set the scene by id."""
        if scene_id in SCENES:
            self.pilot_params["sceneId"] = scene_id
        else:
            # id not in SCENES !
            raise ValueError("Scene is not available. Only 0 to 32 are supported")

    def _set_rgb(self, values):
        """Set the RGB color state of the bulb."""
        red, green, blue = values
        if red >= 0 and red < 256:
            self.pilot_params["r"] = red
        else:
            raise ValueError("Red is not in range between 0-255.")
        if green >= 0 and green < 256:
            self.pilot_params["g"] = green
        else:
            raise ValueError("Green is not in range between 0-255.")
        if blue >= 0 and blue < 256:
            self.pilot_params["b"] = blue
        else:
            raise ValueError("Blue is not in range between 0-255.")

    def _set_brightness(self, value: int):
        """Set the value of the brightness 0-255."""
        percent = self.hex_to_percent(value)
        # lamp doesn't supports lower than 10%
        if percent < 10:
            percent = 10
        if percent > 101:
            raise ValueError("Max value can be 100% with 255.")
        self.pilot_params["dimming"] = percent

    def _set_colortemp(self, kelvin: int):
        """Set the color temperature for the white led in the bulb."""
        # normalize the kelvin values - should be removed
        if kelvin < 1000:
            kelvin = 1000
        if kelvin > 10000:
            kelvin = 10000

        self.pilot_params["temp"] = kelvin

    def hex_to_percent(self, hex):
        """Convert hex 0-255 values to percent."""
        return round((hex / 255) * 100)


class PilotParser:
    """Interpret the message from the bulb."""

    def __init__(self, pilotResult):
        """Init the class."""
        self.pilotResult = pilotResult

    def get_state(self) -> bool:
        """Return the state of the bulb."""
        if "state" in self.pilotResult:
            return self.pilotResult["state"]
        else:
            return None

    def get_mac(self) -> str:
        """Return MAC from the bulb."""
        if "mac" in self.pilotResult:
            return self.pilotResult["mac"]
        else:
            return None

    def get_warm_white(self) -> int:
        """Get the value of the warm white led."""
        if "w" in self.pilotResult:
            return self.pilotResult["w"]
        else:
            return None

    def get_white_range(self) -> list:
        """Get the value of the whiteRange property."""
        if "whiteRange" in self.pilotResult:
            return self.pilotResult["whiteRange"]
        else:
            return None

    def get_extended_white_range(self) -> list:
        """Get the value of the extende whiteRange property."""
        if "extRange" in self.pilotResult:
            return self.pilotResult["extRange"]
        # New after v1.22 FW - "cctRange":[2200,2700,6500,6500]
        elif "cctRange" in self.pilotResult:
            return self.pilotResult["cctRange"]
        else:
            return None

    def get_speed(self) -> int:
        """Get the color changing speed."""
        if "speed" in self.pilotResult:
            return self.pilotResult["speed"]
        else:
            return None

    def get_scene(self) -> str:
        """Get the current scene name."""
        if "schdPsetId" in self.pilotResult:  # rhythm
            return SCENES[1000]

        id = self.pilotResult["sceneId"]
        if id in SCENES:
            return SCENES[id]
        else:
            return None

    def get_cold_white(self) -> int:
        """Get the value of the cold white led."""
        if "c" in self.pilotResult:
            return self.pilotResult["c"]
        else:
            return None

    def get_rgb(self):
        """Get the RGB color state of the bulb and turns it on."""
        if (
            "r" in self.pilotResult
            and "g" in self.pilotResult
            and "b" in self.pilotResult
        ):
            r = self.pilotResult["r"]
            g = self.pilotResult["g"]
            b = self.pilotResult["b"]
            return r, g, b
        else:
            # no RGB color value was set
            return None, None, None

    def get_brightness(self) -> int:
        """Get the value of the brightness 0-255."""
        if "dimming" in self.pilotResult:
            return self.percent_to_hex(self.pilotResult["dimming"])

    def get_colortemp(self) -> int:
        """Get the color temperatur from the bulb."""
        if "temp" in self.pilotResult:
            return self.pilotResult["temp"]
        else:
            return None

    def percent_to_hex(self, percent):
        """Convert percent values 0-100 into hex 0-255."""
        return round((percent / 100) * 255)


class wizlight:
    """Create an instance of a WiZ Light Bulb."""

    # default port for WiZ lights

    def __init__(self, ip, connect_on_init=False, port=38899, mac=None):
        """Create instance with the IP address of the bulb."""
        self.ip = ip
        self.port = port
        self.state = None
        self.mac = mac
        self.bulbtype: BulbType = None
        self.whiteRange = None
        self.extwhiteRange = None
        # check the state on init
        if connect_on_init:
            self._check_connection()

    @property
    def status(self) -> bool:
        """Return the status of the bulb: true = on, false = off."""
        if self.state is None:
            return None
        return self.state.get_state()

    # ------------------ Non properties --------------

    def _check_connection(self):
        """Check the connection to the bulb."""
        message = r'{"method":"getPilot","params":{}}'
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        try:
            # send a udp package
            sock.sendto(bytes(message, "utf-8"), (self.ip, self.port))
            # get the data to
            data, addr = sock.recvfrom(1024)
            if data:
                return
        except socket.timeout:
            raise WizLightTimeOutError(
                "No connection was established by initialization."
            )

    async def get_bulbtype(self) -> BulbType:
        """Retrun the bulb type as BulbType object."""
        if self.bulbtype is None:
            bulb_config = await self.getBulbConfig()
            if "moduleName" in bulb_config["result"]:
                _bulbtype = bulb_config["result"]["moduleName"]
                # set the minimum features for dimmable bulbs (DW bulbs)
                # define the kelvin range
                _kelvin = await self.getExtendedWhiteRange()
                # use only first and last entry - [2200,2700,6500,6500]
                _kelvin = _kelvin[:: len(_kelvin) - 1]
                _bulb = BulbType(
                    bulb_type=BulbClass.DW,
                    name=_bulbtype,
                    features=Features(
                        brightness=True, color=False, effect=False, color_tmp=False
                    ),
                    kelvin_range=None,
                )
                try:
                    # parse the features from name
                    _identifier = _bulbtype.split("_")[1]
                # Throw exception if index can not be found
                except IndexError:
                    raise WizLightNotKnownBulb("The bulb type can not be determined!")
                # go an try to map extensions to the BulbTyp object
                # Color support
                if "RGB" in _identifier:
                    _bulb.kelvin_range = KelvinRange(min=_kelvin[0], max=_kelvin[1])
                    _bulb.bulb_type = BulbClass.RGB
                    _bulb.features.color = True
                    # RGB supports effects and tuneabel white
                    _bulb.features.effect = True
                    _bulb.features.color_tmp = True
                # Non RGB but tunable white bulb
                if "TW" in _identifier:
                    _bulb.kelvin_range = KelvinRange(min=_kelvin[0], max=_kelvin[1])
                    _bulb.kelvin_range = KelvinRange(min=2700, max=6500)
                    _bulb.bulb_type = BulbClass.TW
                    _bulb.features.color_tmp = True
                    # RGB supports effects but only "some"
                    # TODO: Improve the mapping to supported effects
                    _bulb.features.effect = True

                self.bulbtype = _bulb
                return _bulb
            raise WizLightNotKnownBulb("The bulb features can not be mapped!")

    async def getWhiteRange(self):
        """Read the white range from the bulb."""
        resp = await self.getUserConfig()
        if resp is not None and "result" in resp and self.whiteRange is None:
            self.whiteRange = PilotParser(resp["result"]).get_white_range()
        else:
            self.whiteRange = None
        return self.whiteRange

    async def getExtendedWhiteRange(self):
        """Read extended withe range from the RGB bulb."""

        # First for FW > 1.22
        resp = await self.getModelConfig()
        if resp is not None and "result" in resp and self.extwhiteRange is None:
            self.extwhiteRange = PilotParser(resp["result"]).get_extended_white_range()
            return self.extwhiteRange
        else:
            # For old FW < 1.22
            resp = await self.getUserConfig()
            if "result" in resp and self.extwhiteRange is None:
                self.extwhiteRange = PilotParser(
                    resp["result"]
                ).get_extended_white_range()
                return self.extwhiteRange
            else:
                self.extwhiteRange = None

    async def getSupportedScenes(self):
        """Return the supported scenes based on type.

        Lookup: https://docs.pro.wizconnected.com
        """
        if self.bulbtype is None:
            await self.get_bulbtype()
        # retrun for TW
        if self.bulbtype.bulb_type == BulbClass.TW:
            return [
                SCENES[key]
                for key in [6, 9, 10, 11, 12, 13, 14, 15, 16, 18, 29, 30, 31, 32]
            ]
        if self.bulbtype.bulb_type == BulbClass.DW:
            return [SCENES[key] for key in [9, 10, 13, 14, 29, 30, 31, 32]]
        # Must be RGB with all
        return SCENES

    async def turn_off(self):
        """Turn the light off."""
        message = r'{"method":"setPilot","params":{"state":false}}'
        await self.sendUDPMessage(message)

    async def reboot(self):
        """Reboot the bulb."""
        message = r'{"method":"reboot","params":{}}'
        await self.sendUDPMessage(message)

    async def reset(self):
        """Reset the bulb to factory defaults."""
        message = r'{"method":"reset","params":{}}'
        await self.sendUDPMessage(message)

    async def turn_on(self, pilot_builder=PilotBuilder()):
        """Turn the light on with defined message.

        :param pilot_builder: PilotBuilder object to set the turn on state, defaults to PilotBuilder()
        :type pilot_builder: [type], optional
        """
        await self.sendUDPMessage(pilot_builder.set_pilot_message())

    async def set_state(self, pilot_builder=PilotBuilder()):
        """Set the state of the bulb with defined message. Doesn't turns on the light.

        :param pilot_builder: PilotBuilder object to set the state, defaults to PilotBuilder()
        :type pilot_builder: [type], optional
        """
        await self.sendUDPMessage(pilot_builder.set_state_message(self.status))

    def get_id_from_scene_name(self, scene: str) -> int:
        """Retrun the id of an given scene name.

        :param scene: Name of the scene
        :type scene: str
        :raises ValueError: Retrun if not in scene list
        :return: ID of the scene
        :rtype: int
        """
        for id in SCENES:
            if SCENES[id] == scene:
                return id
        raise ValueError("Scene '%s' not in scene list." % scene)

    # ---------- Helper Functions ------------
    async def updateState(self):
        """Update the bulb state.

        Note: Call this method before getting any other property.
        Also, call this method to update the current value for any property.
        getPilot - gets the current bulb state - no paramters need to be included
        {"method": "getPilot", "id": 24}
        """
        message = r'{"method":"getPilot","params":{}}'
        resp = await self.sendUDPMessage(message)
        if resp is not None and "result" in resp:
            self.state = PilotParser(resp["result"])
        else:
            self.state = None
        return self.state

    async def getMac(self):
        """Read the MAC from the bulb."""
        resp = await self.getBulbConfig()
        if resp is not None and "result" in resp and self.mac is None:
            self.mac = PilotParser(resp["result"]).get_mac()
        else:
            self.mac = None
        return self.mac

    async def getBulbConfig(self):
        """Return the configuration from the bulb."""
        message = r'{"method":"getSystemConfig","params":{}}'
        return await self.sendUDPMessage(message)

    async def getModelConfig(self):
        """Return the new model capabilities from the bulb.
        Only available in bulb FW >1.22!
        """
        try:
            message = r'{"method":"getModelConfig","params":{}}'
            return await self.sendUDPMessage(message)
        except WizLightMethodeNotFound:
            return None

    async def getUserConfig(self):
        """Return the user configuration from the bulb."""
        message = r'{"method":"getUserConfig","params":{}}'
        return await self.sendUDPMessage(message)

    async def lightSwitch(self):
        """Turn the light bulb on or off like a switch."""
        # first get the status
        state = await self.updateState()
        if state.get_state():
            # if the light is on - switch off
            await self.turn_off()
        else:
            # if the light is off - turn on
            await self.turn_on()

    async def receiveUDPwithTimeout(self, stream, timeout):
        """Get messtage with timout value."""
        data, remote_addr = await asyncio.wait_for(stream.recv(), timeout)
        return data

    async def sendUDPMessage(self, message):
        """Send the UDP message to the bulb."""
        connid = hex(int(time() * 10000000))[2:]
        data = None
        # overall 10 sec. for time out
        timeout = 10
        send_interval = 0.5
        max_send_datagrams = int(timeout / send_interval)

        try:
            _LOGGER.debug(
                "[wizlight {}, connid {}] connecting to UDP port with send_interval of {} sec..".format(
                    self.ip, connid, send_interval
                )
            )
            stream = await asyncio.wait_for(
                asyncio_dgram.connect((self.ip, self.port)), timeout
            )
            _LOGGER.debug(
                "[wizlight {}, connid {}] listening for response datagram".format(
                    self.ip, connid
                )
            )

            receive_task = asyncio.create_task(
                self.receiveUDPwithTimeout(stream, timeout)
            )

            for i in range(max_send_datagrams):
                _LOGGER.debug(
                    "[wizlight {}, connid {}] sending command datagram {}: {}".format(
                        self.ip, connid, i, message
                    )
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
                "[wizlight {}, connid {}] Failed to do UDP call(s) to wiz light - Timeout Error!".format(
                    self.ip, connid
                ),
                exc_info=False,
            )
            raise WizLightTimeOutError("The request to the bulb timed out")
        finally:
            try:
                stream.close()
            except UnboundLocalError:
                raise WizLightConnectionError(
                    "Bulb is offline or IP address is not correct."
                )

        if data is not None and len(data) is not None:
            resp = json.loads(data.decode())
            if "error" not in resp:
                _LOGGER.debug(
                    "[wizlight {}, connid {}] response received: {}".format(
                        self.ip, connid, resp
                    )
                )
                return resp
            elif resp["error"]["code"] == -32601:
                raise WizLightMethodeNotFound(
                    "Cant found the methode. Maybe older bulb FW?"
                )
            # exception should be created
            raise ValueError("Can't read response from the bulb. Debug:", resp)
