"""Tests for signed requests on "env":"pro" firmware."""

import asyncio
import base64
import hashlib
import hmac
import json
import time
from typing import Any, AsyncGenerator, Dict, Tuple

import pytest

from pywizlight import PilotBuilder, wizlight
from pywizlight.exceptions import WizLightConnectionError
from pywizlight.utils import sign_request

KEY_HEX = "00112233445566778899aabbccddeeff"
KEY = bytes.fromhex(KEY_HEX)


def _mac(obj: Dict[str, Any]) -> str:
    payload = json.dumps(obj, separators=(",", ":")).encode()
    return base64.b64encode(hmac.new(KEY, payload, hashlib.sha256).digest()).decode()


def test_sign_request_known_answer() -> None:
    """The signature covers compact params including sigTs."""
    signed = sign_request(
        {"method": "setPilot", "params": {"state": True}}, KEY, timestamp=1790441723
    )
    assert signed == {
        "method": "setPilot",
        "env": "pro",
        "params": {"state": True, "sigTs": 1790441723},
        "hmac": "vARMv4JpVsxYabcBovABd25ISBzYT8+71v0CUtpU1sg=",
    }


def test_sign_request_leaves_input_alone() -> None:
    msg = {"method": "setPilot", "params": {"dimming": 50}}
    sign_request(msg, KEY)
    assert msg == {"method": "setPilot", "params": {"dimming": 50}}


class SignedBulb(asyncio.DatagramProtocol):
    """Answers like fw 1.39 on ESP25_SHORGB_01: reads open, writes signed."""

    def __init__(self) -> None:
        self.pilot: Dict[str, Any] = {"mac": "a8bb5006033d", "state": False}
        self.transport: asyncio.DatagramTransport

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self.transport = transport  # type: ignore[assignment]

    def _reply(self, method: str, key: str, body: Dict[str, Any], addr: Any) -> None:
        body = {**body, "sigTs": int(time.time())}
        resp = {"method": method, "env": "pro", key: body, "hmac": _mac(body)}
        self.transport.sendto(json.dumps(resp, separators=(",", ":")).encode(), addr)

    def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
        req = json.loads(data)
        method, params = req["method"], req.get("params", {})
        if method == "getPilot":
            self._reply(method, "result", self.pilot, addr)
            return
        if method == "getSystemConfig":
            config = {"moduleName": "ESP25_SHORGB_01", "fwVersion": "1.39.0"}
            self._reply(method, "result", config, addr)
            return
        if method == "getModelConfig":
            model = {
                "devTotal": 1,
                "headTotal": 1,
                "cctRange": [2700, 2700, 5000, 5000],
            }
            self._reply(method, "result", model, addr)
            return
        if method == "getUserConfig":
            self._reply(method, "result", {"fadeIn": 500, "fadeOut": 2000}, addr)
            return
        if method.startswith("get"):
            not_found = {"code": -32601, "message": "Method not found"}
            self._reply(method, "error", not_found, addr)
            return
        if "sigTs" not in params:
            self._reply(
                method, "error", {"code": -32602, "message": "Invalid params"}, addr
            )
            return
        if req.get("hmac") != _mac(params) or time.time() - params["sigTs"] > 30:
            self._reply(
                method, "error", {"code": -32605, "message": "Security error"}, addr
            )
            return
        self.pilot.update({k: v for k, v in params.items() if k != "sigTs"})
        self._reply(method, "result", {"success": True}, addr)


@pytest.fixture()
async def signed_bulb_port() -> AsyncGenerator[int, None]:
    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(
        SignedBulb, local_addr=("127.0.0.1", 0)
    )
    yield transport.get_extra_info("sockname")[1]
    transport.close()


@pytest.mark.asyncio
async def test_unsigned_write_is_rejected(signed_bulb_port: int) -> None:
    bulb = wizlight(ip="127.0.0.1", port=signed_bulb_port)
    with pytest.raises(WizLightConnectionError, match="-32602"):
        await bulb.turn_on(PilotBuilder(brightness=128))
    await bulb.async_close()


@pytest.mark.asyncio
async def test_wrong_key_is_rejected(signed_bulb_port: int) -> None:
    bulb = wizlight(ip="127.0.0.1", port=signed_bulb_port, signing_key="ff" * 16)
    with pytest.raises(WizLightConnectionError, match="-32605"):
        await bulb.turn_on(PilotBuilder(brightness=128))
    await bulb.async_close()


@pytest.mark.asyncio
async def test_signed_write_and_read(signed_bulb_port: int) -> None:
    bulb = wizlight(ip="127.0.0.1", port=signed_bulb_port, signing_key=KEY_HEX)
    await bulb.turn_on(PilotBuilder(brightness=128, colortemp=2700))
    states = await bulb.updateState()
    assert states and states[0]
    assert states[0].get_state() is True
    assert states[0].get_colortemp() == 2700
    await bulb.async_close()
