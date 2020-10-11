"""pywizlight integration."""
import asyncio
import json
import logging
import socket
from time import time

import asyncio_dgram

from pywizlight.scenes import SCENES

_LOGGER = logging.getLogger(__name__)
FOUND_BULB_IPS = []


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
    ):
        """Set the parameter."""
        self.pilot_params = {"state": True}

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

    def get_pilot_message(self):
        """Retrun the pilot message."""
        return json.dumps({"method": "setPilot", "params": self.pilot_params})

    def _set_warm_white(self, value: int):
        """Set the value of the cold white led."""
        if value > 0 and value < 256:
            self.pilot_params["w"] = value

    def _set_cold_white(self, value: int):
        """Set the value of the cold white led."""
        if value > 0 and value < 256:
            self.pilot_params["c"] = value
        else:
            raise IndexError("Value must be between 1 and 255")

    def _set_speed(self, value: int):
        """Set the color changing speed in precent (0-100).This applies only to changing effects."""
        if value > 0 and value < 101:
            self.pilot_params["speed"] = value
        else:
            raise IndexError("Value must be between 0 and 100")

    def _set_scene(self, scene_id: int):
        """Set the scene by id."""
        if scene_id in SCENES:
            self.pilot_params["sceneId"] = scene_id
        else:
            # id not in SCENES !
            raise IndexError("Scene is not available - only 0 to 32 are supported")

    def _set_rgb(self, values):
        """Set the rgb color state of the bulb."""
        r, g, b = values
        self.pilot_params["r"] = r
        self.pilot_params["g"] = g
        self.pilot_params["b"] = b

    def _set_brightness(self, value: int):
        """Set the value of the brightness 0-255."""
        percent = self.hex_to_percent(value)
        # lamp doesn't supports lower than 10%
        if percent < 10:
            percent = 10
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
    """PilotParser Class - interprets the mesage from the bulb."""

    def __init__(self, pilotResult):
        """Init the class."""
        self.pilotResult = pilotResult

    def get_state(self) -> str:
        """Return the state of the bulb."""
        return self.pilotResult["state"]

    def get_mac(self) -> str:
        """Retrun MAC from the bulb."""
        return self.pilotResult["mac"]

    def get_warm_white(self) -> int:
        """Get the value of the warm white led."""
        if "w" in self.pilotResult:
            return self.pilotResult["w"]
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
        """Get the rgb color state of the bulb and turns it on."""
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
    """Create a instance of a WiZ Light Bulb."""

    # default port for WiZ lights

    def __init__(self, ip, port=38899):
        """Create instance with ip of the bulb."""
        self.ip = ip
        self.port = port
        self.state = None
        self.mac = None

    @property
    def status(self) -> bool:
        """Return true or false / true = on , false = off."""
        if self.state is None:
            return None
        return self.state.get_state()

    # ------------------ Non properties --------------

    async def turn_off(self):
        """Turn the light off."""
        message = r'{"method":"setPilot","params":{"state":false}}'
        await self.sendUDPMessage(message)

    async def turn_on(self, pilot_builder=PilotBuilder()):
        """Turn the light on."""
        await self.sendUDPMessage(
            pilot_builder.get_pilot_message(), max_send_datagrams=10
        )

    def get_id_from_scene_name(self, scene: str) -> int:
        """Get the id from a scene name."""
        for id in SCENES:
            if SCENES[id] == scene:
                return id
        raise ValueError("Scene '%s' not in scene list." % scene)

    # ---------- Helper Functions ------------
    async def updateState(self):
        """Update the bulb state."""
        """
            Note: Call this method before getting any other property
            Also, call this method to update the current value for any property
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
        if resp is not None and "result" in resp:
            self.mac = PilotParser(resp["result"]).get_mac()
        else:
            self.mac = None
        return self.mac

    async def getBulbConfig(self):
        """Return the configuration from the bulb."""
        message = r'{"method":"getSystemConfig","params":{}}'
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

    async def sendUDPMessage(
        self, message, timeout=60, send_interval=0.5, max_send_datagrams=100
    ):
        """Send the udp message to the bulb."""
        connid = hex(int(time() * 10000000))[2:]
        data = None

        try:
            _LOGGER.debug(
                "[wizlight {}, connid {}] connecting to UDP port".format(
                    self.ip, connid
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

            i = 0
            while not receive_task.done() and i < max_send_datagrams:
                _LOGGER.debug(
                    "[wizlight {}, connid {}] sending command datagram {}: {}".format(
                        self.ip, connid, i, message
                    )
                )
                asyncio.create_task(stream.send(bytes(message, "utf-8")))
                await asyncio.sleep(send_interval)
                i += 1

            await receive_task
            data = receive_task.result()

        except asyncio.TimeoutError:
            _LOGGER.exception(
                "[wizlight {}, connid {}] Failed to do UDP call(s) to wiz light".format(
                    self.ip, connid
                ),
                exc_info=False,
            )
        finally:
            stream.close()

        if data is not None and len(data) is not None:
            resp = json.loads(data.decode())
            if "error" not in resp:
                _LOGGER.debug(
                    "[wizlight {}, connid {}] response received: {}".format(
                        self.ip, connid, resp
                    )
                )
                return resp
            else:
                # exception should be created
                raise ValueError("Cant read response from the bulb. Debug:", resp)


class discovery:
    """Discover bulbs via network broadcast."""

    class BroadcastProtocol(object):
        """asyncio Protocol that sends a UDP broadcast message for bulb discovery."""

        def __init__(self, loop):
            """Init discovery function."""
            self.loop = loop

        def connection_made(self, transport):
            """Init connection to socket and register broadcasts."""
            self.transport = transport
            sock = transport.get_extra_info("socket")
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.broadcast_registration()

        def broadcast_registration(self):
            """Send a registration method as UDP broadcast."""
            """Note: The ip and mac we give the bulb here don't seem to matter for our
            intents and purposes, so they're hardcoded to technically valid dummy data."""

            """Fix for async problems if boardcast_registration is called twice! See #13."""
            """dirty dirty hack."""
            try:
                register_method = r'{"method":"registration","params":{"phoneMac":"AAAAAAAAAAAA","register":false,"phoneIp":"1.2.3.4","id":"1"}}'  # noqa: E501
                self.transport.sendto(
                    register_method.encode(), ("255.255.255.255", 38899)
                )
                self.loop.call_later(1, self.broadcast_registration)
            except AttributeError:
                pass

        def datagram_received(self, data, addr):
            """Receive data from broadcast."""
            _LOGGER.debug(
                "received data {} from addr {} on UPD discovery port".format(data, addr)
            )
            if """"success":true""" in data.decode():
                ip = addr[0]
                global FOUND_BULB_IPS
                if ip not in FOUND_BULB_IPS:
                    _LOGGER.debug("Found bulb at IP: {}".format(ip))
                    FOUND_BULB_IPS.append(ip)

        def connection_lost(self, exc):
            """Retrun connection error."""
            _LOGGER.debug("closing udp discovery")

    async def find_wizlights(self, wait_time=5) -> list:
        """Start discovery and return list of wizlight objects."""
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: self.BroadcastProtocol(loop), local_addr=("0.0.0.0", 38899)
        )
        try:
            await asyncio.sleep(wait_time)
        finally:
            transport.close()
            return [wizlight(ip) for ip in FOUND_BULB_IPS]
