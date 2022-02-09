"""Tests for the Scenes."""


import pytest

from pywizlight import scenes


@pytest.mark.asyncio
async def test_get_id_from_scene_name() -> None:
    """Test looking up a scene id from the name."""
    with pytest.raises(ValueError):
        scenes.get_id_from_scene_name("non_exist")
    assert scenes.get_id_from_scene_name("Ocean") == 1
