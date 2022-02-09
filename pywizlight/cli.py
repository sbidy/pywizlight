"""Command-line interface to interact with wizlight devices."""
import asyncio
from functools import wraps
from typing import Any, Callable, Coroutine, TypeVar

import click

from pywizlight import PilotBuilder, discovery, wizlight

T = TypeVar("T")


def coro(f: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    """Allow to use async in click."""

    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        """Async wrapper."""
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
@click.version_option()
def main() -> None:
    """Command-line tool to interact with Wizlight bulbs."""


@main.command("discover")
@coro
@click.option(
    "--b",
    prompt="Set the broadcast address",
    help="Define the broadcast address like 192.168.1.255.",
)
async def discover(b: str) -> None:
    """Discovery bulb in the local network."""
    click.echo(f"Search for bulbs in {b} ... ")

    bulbs = await discovery.find_wizlights(broadcast_address=b)
    for bulb in bulbs:
        click.echo(bulb.__dict__)


@main.command("on")
@coro
@click.option("--ip", prompt="IP address of the bulb", help="IP address of the bulb.")
@click.option(
    "--k",
    prompt="Kelvin for temperature.",
    help="Kelvin value (1000-8000) for turn on. Default 3000",
    default=3000,
    type=int,
)
@click.option(
    "--brightness",
    prompt="Set the brightness value 0-255",
    help="Brightness for turn on. Default 128",
    default=128,
    type=int,
)
async def turn_on(ip: str, k: int, brightness: int) -> None:
    """Turn a given bulb on."""
    click.echo(f"Turning on {ip}")
    bulb = wizlight(ip)
    if bulb and 1000 <= k <= 6800 and 0 <= brightness <= 255:
        await bulb.turn_on(PilotBuilder(colortemp=k, brightness=brightness))
    else:
        click.echo("Error - values are not correct. Type --help for help.")


@main.command("set-state")
@coro
@click.option("--ip", prompt="IP address of the bulb", help="IP address of the bulb.")
@click.option(
    "--k",
    prompt="Kelvin for temperature.",
    help="Kelvin value (1000-8000) for turn on. Default 3000",
    default=3000,
)
@click.option(
    "--brightness",
    prompt="Set the brightness value 0-255",
    help="Brightness for turn on. Default 128",
    default=128,
)
async def set_state(ip: str, k: int, brightness: int) -> None:
    """Set the current state of a given bulb."""
    click.echo(f"Turning on {ip}")
    bulb = wizlight(ip)
    if bulb and 1000 <= k <= 6800 and 0 <= brightness <= 255:
        await bulb.set_state(PilotBuilder(colortemp=k, brightness=brightness))
    else:
        click.echo("Error - values are not correct. Type --help for help.")


@main.command("off")
@coro
@click.option("--ip", prompt="IP address of the bulb", help="IP address of the bulb.")
async def turn_off(ip: str) -> None:
    """Turn a given bulb off."""
    click.echo(f"Turning off {ip}")
    bulb = wizlight(ip)
    await bulb.turn_off()


@main.command("state")
@coro
@click.option("--ip", prompt="IP address of the bulb", help="IP address of the bulb.")
async def state(ip: str) -> None:
    """Get the current state of a given bulb."""
    click.echo(f"Get the state from {ip}")
    bulb_state = await wizlight(ip).updateState()
    if bulb_state:
        click.echo(bulb_state.pilotResult)
    else:
        click.echo("Did not get state from bulb")


if __name__ == "__main__":
    main()
