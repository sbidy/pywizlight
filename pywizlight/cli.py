"""Command-line interface to interact with wizlight devices."""
import asyncio
from functools import wraps

import click

from pywizlight import PilotBuilder, discovery, wizlight


def coro(f):
    """Allow to use async in click."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        """Async wrapper."""
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
@click.version_option()
def main():
    """Command-line tool to interact with Wizlight bulbs."""


@main.command("discover")
@coro
@click.option(
    "--b",
    prompt="Set the broadcast address",
    help="Define the broadcast address like 192.168.1.255.",
)
async def discover(b):
    """Disocvery bulb in the local network."""
    click.echo(f"Search for bulbs in {b} ... ")

    bulbs = await discovery.find_wizlights(broadcast_address=b)
    for bulb in bulbs:
        click.echo(bulb.__dict__)


@main.command("on")
@coro
@click.option("--ip", prompt="IP address of the bulb", help="IP address of the bulb.")
@click.option(
    "--k",
    prompt="Kelvin for temperatur.",
    help="Kelvin value (1000-8000) for turn on. Default 3000k",
    default=3000,
)
@click.option(
    "--brightness",
    prompt="Set the brightness value 0-255",
    help="Brightness for turn on. Default 128",
    default=128,
)
async def turn_on(ip, k, brightness):
    """Turn a given bulb on."""
    click.echo("Turning on %s" % ip)
    bulb = wizlight(ip)
    if bulb and k <= 6800 and k >= 1000 and brightness >= 0 and brightness <= 256:
        await bulb.turn_on(PilotBuilder(colortemp=k, brightness=brightness))
    else:
        click.echo("Error - values are not correct. Type --help for help.")


@main.command("set-state")
@coro
@click.option("--ip", prompt="IP address of the bulb", help="IP address of the bulb.")
@click.option(
    "--k",
    prompt="Kelvin for temperatur.",
    help="Kelvin value (1000-8000) for turn on. Default 3000k",
    default=3000,
)
@click.option(
    "--brightness",
    prompt="Set the brightness value 0-255",
    help="Brightness for turn on. Default 128",
    default=128,
)
async def set_state(ip, k, brightness):
    """Turn a given bulb on."""
    click.echo("Turning on %s" % ip)
    bulb = wizlight(ip)
    if bulb and k <= 6800 and k >= 1000 and brightness >= 0 and brightness <= 256:
        await bulb.set_state(PilotBuilder(colortemp=k, brightness=brightness))
    else:
        click.echo("Error - values are not correct. Type --help for help.")


@main.command("off")
@coro
@click.option("--ip", prompt="IP address of the bulb", help="IP address of the bulb.")
async def turn_off(ip):
    """Turn a given bulb off."""
    click.echo("Turning off %s" % ip)
    bulb = wizlight(ip)
    await bulb.turn_off()


@main.command("state")
@coro
@click.option("--ip", prompt="IP address of the bulb", help="IP address of the bulb.")
async def state(ip):
    """Get the current state of a given bulb."""
    click.echo("Get the state from %s" % ip)
    bulb = wizlight(ip)
    state = await bulb.updateState()
    click.echo(state.__dict__["pilotResult"])


if __name__ == "__main__":
    main()
