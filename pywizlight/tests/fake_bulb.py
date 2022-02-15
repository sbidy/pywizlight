"""Start up a fake bulb to test features without a real bulb."""
import asyncio
import json
from typing import Any, Callable, Dict, Tuple, cast

from pywizlight.protocol import WizProtocol

MODULE_CONFIGS = {  # AKA getModelConfig
    ("ESP01_SHRGB_03", "1.25.0"): {
        "method": "getModelConfig",
        "env": "pro",
        "result": {
            "ps": 1,
            "pwmFreq": 1000,
            "pwmRange": [3, 100],
            "wcr": 30,
            "nowc": 1,
            "cctRange": [2200, 2700, 4800, 6500],
            "renderFactor": [171, 255, 75, 255, 43, 85, 0, 0, 0, 0],
        },
    },
    ("ESP10_SOCKET_06", "1.25.0"): {
        "method": "getModelConfig",
        "env": "pro",
        "result": {
            "ps": 1,
            "pwmFreq": 200,
            "pwmRange": [1, 100],
            "wcr": 20,
            "nowc": 2,
            "cctRange": [2700, 2700, 2700, 2700],
            "renderFactor": [255, 0, 255, 255, 0, 0, 0, 0, 0, 0],
        },
    },
    ("ESP05_SHDW_21", "1.25.0"): {
        "method": "getModelConfig",
        "env": "pro",
        "result": {
            "ps": 1,
            "pwmFreq": 1000,
            "pwmRange": [5, 100],
            "wcr": 20,
            "nowc": 1,
            "cctRange": [2700, 2700, 2700, 2700],
            "renderFactor": [255, 0, 255, 255, 0, 0, 0, 0, 0, 0],
        },
    },
    ("ESP20_SHRGB_01ABI", "1.25.0"): {
        "method": "getModelConfig",
        "env": "pro",
        "result": {
            "ps": 0,
            "pwmFreq": 2000,
            "pwmRange": [5, 100],
            "wcr": 80,
            "nowc": 2,
            "cctRange": [2700, 2700, 6500, 6500],
            "renderFactor": [255, 0, 255, 255, 0, 0, 0, 81, 245, 178],
            "drvIface": 0,
        },
    },
    ("ESP21_SHTW_01", "1.25.0"): {
        "method": "getModelConfig",
        "env": "pro",
        "result": {
            "ps": 2,
            "pwmFreq": 5000,
            "pwmRange": [1, 100],
            "wcr": 20,
            "nowc": 1,
            "cctRange": [2700, 2700, 5000, 5000],
            "renderFactor": [255, 0, 255, 255, 0, 0, 0, 0, 0, 0],
            "drvIface": 0,
        },
    },
    ("MISSING", "1.16.64"): {
        "method": "getModelConfig",
        "env": "pro",
        "result": {
            "ps": 2,
            "pwmFreq": 5000,
            "pwmRange": [1, 100],
            "wcr": 20,
            "nowc": 1,
            "cctRange": [2700, 2700, 5000, 5000],
            "renderFactor": [255, 0, 255, 255, 0, 0, 0, 0, 0, 0],
            "drvIface": 0,
        },
    },
    ("MISSING_KELVIN", "1.16.64"): {
        "method": "getModelConfig",
        "env": "pro",
        "result": {
            "ps": 2,
            "pwmFreq": 5000,
            "pwmRange": [1, 100],
            "wcr": 20,
            "nowc": 1,
            "renderFactor": [255, 0, 255, 255, 0, 0, 0, 0, 0, 0],
            "drvIface": 0,
        },
    },
    ("INVALID", "1.16.64"): {
        "method": "getModelConfig",
        "env": "pro",
        "result": {
            "ps": 2,
            "pwmFreq": 5000,
            "pwmRange": [1, 100],
            "wcr": 20,
            "nowc": 1,
            "cctRange": [2700, 2700, 5000, 5000],
            "renderFactor": [255, 0, 255, 255, 0, 0, 0, 0, 0, 0],
            "drvIface": 0,
        },
    },
}

SYSTEM_CONFIGS = {  # AKA getSystemConfig
    ("ESP01_SHRGB_03", "1.25.0"): {
        "method": "getSystemConfig",
        "env": "pro",
        "result": {
            "mac": "a8bb5006033d",
            "homeId": 653906,
            "roomId": 989983,
            "moduleName": "ESP01_SHRGB_03",
            "fwVersion": "1.25.0",
            "groupId": 0,
            "drvConf": [30, 1],
            "ewf": [255, 0, 255, 255, 0, 0, 0],
            "ewfHex": "ff00ffff000000",
            "ping": 0,
        },
    },
    ("ESP10_SOCKET_06", "1.25.0"): {
        "method": "getSystemConfig",
        "env": "pro",
        "result": {
            "mac": "a8bb5006033d",
            "homeId": 653906,
            "roomId": 989983,
            "moduleName": "ESP10_SOCKET_06",
            "fwVersion": "1.25.0",
            "groupId": 0,
            "drvConf": [20, 2],
            "ewf": [255, 0, 255, 255, 0, 0, 0],
            "ewfHex": "ff00ffff000000",
            "ping": 0,
        },
    },
    ("ESP05_SHDW_21", "1.25.0"): {
        "method": "getSystemConfig",
        "env": "pro",
        "result": {
            "mac": "a8bb5006033d",
            "homeId": 653906,
            "roomId": 989983,
            "moduleName": "ESP05_SHDW_21",
            "fwVersion": "1.25.0",
            "groupId": 0,
            "drvConf": [20, 1],
            "ewf": [255, 0, 255, 255, 0, 0, 0],
            "ewfHex": "ff00ffff000000",
            "ping": 0,
        },
    },
    ("ESP20_SHRGB_01ABI", "1.25.0"): {
        "method": "getSystemConfig",
        "env": "pro",
        "result": {
            "mac": "a8bb5006033d",
            "homeId": 653906,
            "roomId": 989983,
            "moduleName": "ESP20_SHRGB_01ABI",
            "fwVersion": "1.25.0",
            "groupId": 0,
            "drvConf": [80, 2],
            "ewf": [255, 0, 255, 255, 0, 0, 0],
            "ewfHex": "ff00ffff000000",
            "ping": 0,
        },
    },
    ("ESP20_SHRGB_01ABI", "1.21.4"): {
        "method": "getSystemConfig",
        "env": "pro",
        "result": {
            "mac": "a8bb5006033d",
            "homeId": 653906,
            "roomId": 989983,
            "moduleName": "ESP20_SHRGB_01ABI",
            "fwVersion": "1.21.4",
            "groupId": 0,
            "drvConf": [80, 2],
            "ewf": [255, 0, 255, 255, 0, 0, 0],
            "ewfHex": "ff00ffff000000",
            "ping": 0,
        },
    },
    ("ESP03_SHRGB3_01ABI", "1.16.64"): {
        "method": "getSystemConfig",
        "env": "pro",
        "result": {
            "mac": "a8bb50fd92e5",
            "homeId": 5385975,
            "roomId": 0,
            "homeLock": False,
            "pairingLock": False,
            "typeId": 0,
            "moduleName": "ESP03_SHRGB3_01ABI",
            "fwVersion": "1.16.64",
            "groupId": 0,
            "drvConf": [20, 1],
        },
    },
    ("ESP20_SHRGBC_01", "1.21.4"): {
        "method": "getSystemConfig",
        "env": "pro",
        "result": {
            "mac": "6c2990e493bc",
            "homeId": 5385975,
            "roomId": 8016844,
            "moduleName": "ESP20_SHRGBC_01",
            "fwVersion": "1.21.4",
            "groupId": 0,
            "drvConf": [30, 1],
            "ewf": [200, 255, 150, 255, 0, 0, 40],
            "ewfHex": "c8ff96ff000028",
            "ping": 0,
        },
    },
    ("ESP21_SHTW_01", "1.25.0"): {
        "method": "getSystemConfig",
        "env": "pro",
        "result": {
            "mac": "6c29905a067c",
            "homeId": 5385975,
            "roomId": 8016844,
            "rgn": "eu",
            "moduleName": "ESP21_SHTW_01",
            "fwVersion": "1.25.0",
            "groupId": 0,
            "ping": 0,
        },
    },
    ("MISSING_KELVIN", "1.16.64"): {
        "method": "getSystemConfig",
        "env": "pro",
        "result": {
            "mac": "6c29905a067c",
            "homeId": 5385975,
            "roomId": 8016844,
            "rgn": "eu",
            "moduleName": "ESP21_SHTW_01",
            "fwVersion": "1.25.0",
            "groupId": 0,
            "ping": 0,
        },
    },
    ("MISSING", "1.16.64"): {
        "method": "getSystemConfig",
        "env": "pro",
        "result": {
            "mac": "6c29905a067c",
            "homeId": 5385975,
            "roomId": 8016844,
            "rgn": "eu",
            "fwVersion": "1.25.0",
            "groupId": 0,
            "ping": 0,
        },
    },
    ("INVALID", "1.16.64"): {
        "method": "getSystemConfig",
        "env": "pro",
        "result": {
            "mac": "6c29905a067c",
            "homeId": 5385975,
            "roomId": 8016844,
            "rgn": "eu",
            "moduleName": "INVALID",
            "fwVersion": "1.25.0",
            "groupId": 0,
            "ping": 0,
        },
    },
    ("ESP01_SHRGB1C_31", "1.17.1"): {
        "method": "getSystemConfig",
        "env": "pro",
        "result": {
            "mac": "a8bb50bdf8d7",
            "homeId": 5385975,
            "roomId": 0,
            "homeLock": False,
            "pairingLock": False,
            "typeId": 0,
            "moduleName": "ESP01_SHRGB1C_31",
            "fwVersion": "1.17.1",
            "groupId": 0,
            "drvConf": [20, 2],
        },
    },
    ("ESP14_SHTW1C_01", "1.18.0"): {
        "method": "getSystemConfig",
        "env": "pro",
        "result": {
            "mac": "a8bb503ea5f4",
            "homeId": 5385975,
            "roomId": 0,
            "homeLock": False,
            "pairingLock": False,
            "typeId": 0,
            "moduleName": "ESP14_SHTW1C_01",
            "fwVersion": "1.18.0",
            "groupId": 0,
            "drvConf": [20, 1],
        },
    },
    ("ESP06_SHDW9_01", "1.11.7"): {
        "method": "getSystemConfig",
        "env": "",
        "result": {
            "mac": "a8bb509f71d1",
            "homeId": 0,
            "homeLock": False,
            "pairingLock": False,
            "typeId": 0,
            "moduleName": "ESP06_SHDW9_01",
            "fwVersion": "1.11.7",
            "groupId": 0,
            "drvConf": [20, 1],
        },
    },
}

USER_CONFIGS = {  # AKA getUserConfig
    ("ESP20_SHRGB_01ABI", "1.21.4"): {
        "method": "getUserConfig",
        "env": "pro",
        "result": {
            "fadeIn": 450,
            "fadeOut": 500,
            "dftDim": 100,
            "pwmRange": [0, 100],
            "whiteRange": [2700, 6500],
            "extRange": [2700, 6500],
            "opMode": 0,
            "po": False,
        },
    },
    ("ESP03_SHRGB3_01ABI", "1.16.64"): {
        "method": "getUserConfig",
        "env": "pro",
        "result": {
            "fadeIn": 450,
            "fadeOut": 500,
            "fadeNight": False,
            "dftDim": 100,
            "pwmRange": [0, 100],
            "whiteRange": [2700, 6500],
            "extRange": [2700, 6500],
            "opMode": 0,
            "po": False,
        },
    },
    ("ESP20_SHRGBC_01", "1.21.4"): {
        "method": "getUserConfig",
        "env": "pro",
        "result": {
            "fadeIn": 500,
            "fadeOut": 500,
            "dftDim": 100,
            "pwmRange": [0, 100],
            "whiteRange": [2700, 6500],
            "extRange": [2200, 6500],
            "opMode": 0,
            "po": True,
        },
    },
    ("ESP01_SHRGB1C_31", "1.17.1"): {
        "method": "getUserConfig",
        "env": "pro",
        "result": {
            "fadeIn": 450,
            "fadeOut": 500,
            "fadeNight": False,
            "dftDim": 100,
            "pwmRange": [0, 100],
            "whiteRange": [2700, 6500],
            "extRange": [2700, 6500],
            "po": False,
        },
    },
    ("ESP14_SHTW1C_01", "1.18.0"): {
        "method": "getUserConfig",
        "env": "pro",
        "result": {
            "fadeIn": 450,
            "fadeOut": 500,
            "fadeNight": False,
            "dftDim": 100,
            "pwmRange": [0, 100],
            "whiteRange": [2700, 6500],
            "extRange": [2700, 6500],
            "opMode": 0,
            "po": False,
        },
    },
    ("ESP06_SHDW9_01", "1.11.7"): {
        "method": "getUserConfig",
        "env": "pro",
        "result": {
            "fadeIn": 450,
            "fadeOut": 500,
            "fadeNight": False,
            "dftDim": 100,
            "pwmRange": [0, 100],
            "whiteRange": [2700, 6500],
            "extRange": [2700, 6500],
        },
    },
}


def get_initial_pilot() -> Dict[str, Any]:
    return {
        "method": "getPilot",
        "env": "pro",
        "result": {
            "mac": "ABCABCABCABC",
            "rssi": -62,
            "src": "udp",
            "state": False,
            "sceneId": 0,
            "r": 255,
            "g": 127,
            "b": 0,
            "c": 0,
            "w": 0,
            "temp": 0,
            "dimming": 13,
        },
    }


def get_initial_sys_config(module_name: str, firmware_version: str) -> Dict[str, Any]:
    return SYSTEM_CONFIGS[(module_name, firmware_version)]


def get_initial_model_config(module_name: str, firmware_version: str) -> Dict[str, Any]:
    return MODULE_CONFIGS.get(
        (module_name, firmware_version),
        {
            "method": "getModelConfig",
            "env": "pro",
            "error": {"code": -32601, "message": "Method not found"},
        },
    )


def get_initial_user_config(module_name: str, firmware_version: str) -> Dict[str, Any]:
    return USER_CONFIGS.get(
        (module_name, firmware_version),
        {
            "method": "getUserConfig",
            "env": "pro",
            "error": {"code": -32601, "message": "Method not found"},
        },
    )


BULB_JSON_ERROR = b'{"env":"pro","error":{"code":-32700,"message":"Parse error"}}'


class BulbUDPRequestHandler:
    """Class for UDP handler."""

    pilot_state: Dict[str, Any]  # Will be set by constructor for the actual class
    sys_config: Dict[str, Any]  # Will be set by constructor for the actual class
    model_config: Dict[str, Any]  # Will be set by constructor for the actual class
    user_config: Dict[str, Any]
    registration: Dict[str, Any]
    transport: asyncio.DatagramTransport

    def handle(self, resp: bytes, addr: Tuple[str, int]) -> None:
        """Handle the request."""
        data = resp.strip()
        print(f"Request:{data!r}")
        try:
            json_data: Dict[str, Any] = dict(json.loads(data.decode()))
        except json.JSONDecodeError:
            self.transport.sendto(BULB_JSON_ERROR, addr)
            return

        method = str(json_data["method"])
        if method == "setPilot":
            return_data = self.setPilot(json_data)
            self.transport.sendto(return_data, addr)
        elif method == "getPilot":
            print(f"Response:{json.dumps(self.pilot_state)!r}")
            self.transport.sendto(bytes(json.dumps(self.pilot_state), "utf-8"), addr)
        elif method == "getSystemConfig":
            self.transport.sendto(bytes(json.dumps(self.sys_config), "utf-8"), addr)
        elif method == "getModelConfig":
            self.transport.sendto(bytes(json.dumps(self.model_config), "utf-8"), addr)
        elif method == "getUserConfig":
            self.transport.sendto(bytes(json.dumps(self.user_config), "utf-8"), addr)
        elif method == "registration":
            self.transport.sendto(bytes(json.dumps(self.registration), "utf-8"), addr)
        else:
            raise RuntimeError(f"No handler for {method}")

    def setPilot(self, json_data: Dict[str, Any]) -> bytes:
        """Change the values in the state."""
        for name, value in json_data["params"].items():
            self.pilot_state["result"][name] = value
        return b'{"method":"setPilot","env":"pro","result":{"success":true}}'


async def make_udp_fake_bulb_server(
    module_name: str, firmware_version: str
) -> Tuple[asyncio.BaseTransport, asyncio.BaseProtocol]:
    """Configure a fake bulb instance."""
    handler = BulbUDPRequestHandler()
    handler.pilot_state = get_initial_pilot()
    handler.sys_config = get_initial_sys_config(module_name, firmware_version)
    handler.model_config = get_initial_model_config(module_name, firmware_version)
    handler.user_config = get_initial_user_config(module_name, firmware_version)
    handler.registration = {
        "method": "registration",
        "env": "pro",
        "result": {"mac": "a8bb5006033d", "success": True},
    }

    transport_proto = await asyncio.get_event_loop().create_datagram_endpoint(
        lambda: WizProtocol(on_response=handler.handle),
        local_addr=("127.0.0.1", 0),
    )
    handler.transport = cast(asyncio.DatagramTransport, transport_proto[0])
    return transport_proto


async def make_udp_fake_bulb_push_server() -> Tuple[
    asyncio.BaseTransport, asyncio.BaseProtocol
]:
    """Configure a fake push instance."""
    handler = BulbUDPRequestHandler()
    transport_proto = await asyncio.get_event_loop().create_datagram_endpoint(
        lambda: WizProtocol(on_response=lambda resp, addr: None),
        local_addr=("127.0.0.1", 0),
    )
    handler.transport = cast(asyncio.DatagramTransport, transport_proto[0])
    return transport_proto


async def startup_bulb(
    module_name: str = "ESP01_SHRGB_03", firmware_version: str = "1.25.0"
) -> Tuple[Callable[[], Any], int]:
    """Start up the bulb. Returns a function to shut it down."""
    transport_proto = await make_udp_fake_bulb_server(module_name, firmware_version)
    transport = cast(asyncio.DatagramTransport, transport_proto[0])
    return transport.close, transport.get_extra_info("sockname")[1]
