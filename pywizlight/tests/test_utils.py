"""Tests for the Utils."""


import pytest

from pywizlight import utils


@pytest.mark.asyncio
async def test_generate_mac() -> None:
    """Test generating a mac address."""
    assert len(utils.generate_mac()) == 12


@pytest.mark.asyncio
async def test_get_source_ip() -> None:
    """Test we can get the source ip for loopback."""
    assert utils.get_source_ip("127.0.0.1") == "127.0.0.1"
