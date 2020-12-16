"""Command-line interface to interact with dingz devices."""
import asyncio
from functools import wraps

import click
from pywizlight import wizlight, discovery


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
    """Simple command-line tool to interact with Wizlight bulbs."""


@main.command("discover")
@coro
async def discover():
    """Disocver bulb in the local network."""
    click.echo("Waiting for broadcast packages...")

    bulbs = await discovery.find_wizlights(discovery)
    for bulb in bulbs:
        click.echo(bulb.__dict__)


@main.command("on")
@coro
@click.option("--ip", prompt="IP address of the bulb", help="IP address of the bulb.")
async def turn_on(ip):
    """Turn a given bulb on."""
    click.echo("Turning on %s" % ip)
    bulb = wizlight(ip)
    await bulb.turn_on()


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
