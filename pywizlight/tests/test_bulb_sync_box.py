"""Tests for WiZ HDMI sync box scenes."""

from typing import AsyncGenerator

import pytest

from pywizlight import PilotBuilder, wizlight
from pywizlight.bulb import PilotParser
from pywizlight.bulblibrary import BulbClass
from pywizlight.scenes import SCENES_BY_CLASS, get_id_from_scene_name
from pywizlight.tests.fake_bulb import MODULE_CONFIGS, SYSTEM_CONFIGS, startup_bulb

SYNC_SCENES = [
    (201, "Cinematic"),
    (202, "Vibrant"),
    (203, "Rhythmic"),
    (204, "Relaxation"),
]


@pytest.fixture()
async def sync_box(monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[wizlight, None]:
    """Use capabilities observed on ESP27_MHORGB_01 firmware 1.39.1."""
    key = ("ESP27_MHORGB_01", "1.39.1")
    monkeypatch.setitem(
        SYSTEM_CONFIGS,
        key,
        {
            "method": "getSystemConfig",
            "env": "pro",
            "result": {"moduleName": key[0], "fwVersion": key[1]},
        },
    )
    monkeypatch.setitem(
        MODULE_CONFIGS,
        key,
        {
            "method": "getModelConfig",
            "env": "pro",
            "result": {
                "nowc": 2,
                "wcr": 20,
                "cctRange": [2700, 2700, 6500, 6500],
                "syncboxIfaces": [1, 0, 1, 0],
                "syncboxTvSize": 2,
                "syncboxAlgos": {"201": 3, "202": 16, "203": 256, "204": 4096},
            },
        },
    )
    shutdown, port = await startup_bulb(module_name=key[0], firmware_version=key[1])
    bulb = wizlight(ip="127.0.0.1", port=port)
    try:
        yield bulb
    finally:
        await bulb.async_close()
        shutdown()


@pytest.mark.parametrize(("scene_id", "name"), SYNC_SCENES)
def test_sync_scene_encoding_and_parsing(scene_id: int, name: str) -> None:
    """Sync effects can be selected by name and read from device state."""
    assert get_id_from_scene_name(name) == scene_id
    assert PilotBuilder(scene=scene_id).pilot_params["sceneId"] == scene_id
    assert PilotParser({"sceneId": scene_id}).get_scene() == name


@pytest.mark.asyncio
async def test_supported_sync_scenes(sync_box: wizlight) -> None:
    """Discover sync effects without altering the shared RGB scene list."""
    base_scenes = list(SCENES_BY_CLASS[BulbClass.RGB])
    expected = base_scenes + [name for _, name in SYNC_SCENES]
    assert await sync_box.getSupportedScenes() == expected
    assert await sync_box.getSupportedScenes() == expected
    assert SCENES_BY_CLASS[BulbClass.RGB] == base_scenes
    assert all(name not in base_scenes for _, name in SYNC_SCENES)


@pytest.mark.asyncio
@pytest.mark.parametrize("legacy_markers", [True, False])
@pytest.mark.parametrize(
    ("algorithms", "expected"),
    [
        ({"201": 3, "204": 4096}, ["Cinematic", "Relaxation"]),
        ({"202": 16, "999": 1}, ["Vibrant"]),
        ({}, []),
    ],
)
async def test_advertised_sync_scenes(
    sync_box: wizlight, algorithms: dict, expected: list, legacy_markers: bool
) -> None:
    """An explicit capability map limits the offered sync modes."""
    model_config = await sync_box.getModelConfig()
    assert model_config is not None
    model_config["result"]["syncboxAlgos"] = algorithms
    if not legacy_markers:
        # The algorithm map is sufficient, even without the older box markers.
        model_config["result"].pop("syncboxIfaces")
        model_config["result"].pop("syncboxTvSize")
    assert await sync_box.getSupportedScenes() == (
        SCENES_BY_CLASS[BulbClass.RGB] + expected
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("marker", ["syncboxIfaces", "syncboxTvSize"])
async def test_sync_box_without_algorithm_map(sync_box: wizlight, marker: str) -> None:
    """Recognize older sync-box capability responses reported in issue #187."""
    model_config = await sync_box.getModelConfig()
    assert model_config is not None
    model = model_config["result"]
    model.pop("syncboxAlgos")
    model.pop("syncboxTvSize" if marker == "syncboxIfaces" else "syncboxIfaces")
    if marker == "syncboxIfaces":
        model[marker] = [0, 0, 0, 0]
    assert await sync_box.getSupportedScenes() == (
        SCENES_BY_CLASS[BulbClass.RGB] + [name for _, name in SYNC_SCENES]
    )


@pytest.mark.asyncio
async def test_rgb_without_sync_capabilities(sync_box: wizlight) -> None:
    """A model name containing MHORGB alone does not advertise sync modes."""
    model_config = await sync_box.getModelConfig()
    assert model_config is not None
    for key in ("syncboxAlgos", "syncboxIfaces", "syncboxTvSize"):
        model_config["result"].pop(key)
    scenes = await sync_box.getSupportedScenes()
    assert scenes == SCENES_BY_CLASS[BulbClass.RGB]
    assert all(name not in scenes for _, name in SYNC_SCENES)


@pytest.mark.asyncio
@pytest.mark.parametrize(("scene_id", "name"), SYNC_SCENES)
async def test_sync_scene_round_trip(
    sync_box: wizlight, scene_id: int, name: str
) -> None:
    """Exercise scene selection and state decoding through the UDP transport."""
    await sync_box.turn_on(PilotBuilder(scene=scene_id))
    states = await sync_box.updateState()
    assert states and states[0]
    assert states[0].get_scene_id() == scene_id
    assert states[0].get_scene() == name
