"""Command-line interface to interact with wizlight devices."""

import asyncio
from functools import wraps
from typing import Any, Callable, Coroutine, TypeVar

import click

from  . import PilotBuilder, discovery, wizlight

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
    "--broadcast", "-b",
    default="192.168.1.255",
    help="Broadcast address (default: 192.168.1.255)",
)
async def discover(broadcast: str) -> None:
    """Discover bulbs in the local network."""
    click.echo(f"Searching for bulbs on {broadcast}...")
    
    bulbs = await discovery.find_wizlights(broadcast_address=broadcast)
    if bulbs:
        click.echo(f"Found {len(bulbs)} bulb(s):")
        for bulb in bulbs:
            click.echo(f"  IP: {bulb.ip}, MAC: {bulb.mac}")
    else:
        click.echo("No bulbs found")


@main.command("on")
@coro
@click.argument("ip")
@click.option("--brightness", "-b", default=255, help="Brightness (0-255, default: 255)")
@click.option("--kelvin", "-k", help="Color temperature in Kelvin (1000-6800)")
@click.option("--rgb", help="RGB color as 'r,g,b' (e.g., '255,0,0' for red)")
@click.option("--scene", "-s", type=int, help="Scene ID (1-35)")
@click.option("--device", "-d", type=int, help="Device 1 or 2")
async def turn_on(ip: str, brightness: int, kelvin: int, rgb: str, scene: int, device: int) -> None:
    """Turn bulb on with optional color/brightness settings."""
    bulb = wizlight(ip)
    
    try:
        pilot = PilotBuilder(brightness=brightness, device=device)
        
        if rgb:
            r, g, b = map(int, rgb.split(','))
            pilot = PilotBuilder(rgb=(r, g, b), brightness=brightness, device=device)
        elif kelvin:
            pilot = PilotBuilder(colortemp=kelvin, brightness=brightness, device=device)
        elif scene:
            pilot = PilotBuilder(scene=scene, device=device)
            
        await bulb.turn_on(pilot)
        click.echo(f"✓ Turned on {ip}")
    except Exception as e:
        click.echo(f"✗ Error: {e}")
    finally:
        await bulb.async_close()


@main.command("color")
@coro
@click.argument("ip")
@click.argument("rgb")
@click.option("--brightness", "-b", default=255, help="Brightness (0-255, default: 255)")
@click.option("--device", "-d", type=int, help="Device 1 or 2")
async def set_color(ip: str, rgb: str, brightness: int, device: int) -> None:
    """Set bulb to RGB color (format: 'r,g,b' e.g., '255,0,0')."""
    bulb = wizlight(ip)
    
    try:
        r, g, b = map(int, rgb.split(','))
        await bulb.turn_on(PilotBuilder(rgb=(r, g, b), brightness=brightness, device=device))
        click.echo(f"✓ Set {ip} to RGB({r},{g},{b})")
    except Exception as e:
        click.echo(f"✗ Error: {e}")
    finally:
        await bulb.async_close()


@main.command("off")
@coro
@click.argument("ip")
@click.option("--device", "-d", type=int, help="Device 1 or 2")
async def turn_off(ip: str, device: int) -> None:
    """Turn bulb off."""
    bulb = wizlight(ip)
    
    try:
        await bulb.turn_off(device=device)
        click.echo(f"✓ Turned off {ip}")
    except Exception as e:
        click.echo(f"✗ Error: {e}")
    finally:
        await bulb.async_close()


@main.command("status")
@coro
@click.argument("ip")
async def status(ip: str) -> None:
    """Get bulb status and current settings."""
    bulb = wizlight(ip)
    
    try:
        state = await bulb.updateState()
        if state:
            click.echo(f"Bulb {ip} status:")
            click.echo(f"  Power: {'ON' if state.get_state() else 'OFF'}")
            click.echo(f"  Brightness: {state.get_brightness()}")
            if state.get_rgb():
                r, g, b = state.get_rgb()
                click.echo(f"  RGB: ({r}, {g}, {b})")
            if state.get_colortemp():
                click.echo(f"  Color Temp: {state.get_colortemp()}K")
            if state.get_scene():
                click.echo(f"  Scene: {state.get_scene()}")
        else:
            click.echo(f"✗ Could not get status from {ip}")
    except Exception as e:
        click.echo(f"✗ Error: {e}")
    finally:
        await bulb.async_close()


@main.command("scene")
@coro
@click.argument("ip")
@click.argument("scene_id", type=int)
@click.option("--speed", "-s", type=int, default=128)
@click.option("--device", "-d", type=int, help="Device 1 or 2")
async def set_scene(ip: str, scene_id: int, speed: int, device: int) -> None:
    """Set bulb to a predefined scene (1-35)."""
    bulb = wizlight(ip)
    
    try:
        await bulb.turn_on(PilotBuilder(scene=scene_id, speed=speed, device=device))
        click.echo(f"✓ Set {ip} to scene {scene_id} with speed {speed} on device {device}")
    except Exception as e:
        click.echo(f"✗ Error: {e}")
    finally:
        await bulb.async_close()


@main.command("brightness")
@coro
@click.argument("ip")
@click.argument("level", type=int)
@click.option("--device", "-d", type=int, help="Device 1 or 2")
async def set_brightness(ip: str, level: int, device: int) -> None:
    """Set bulb brightness (0-255)."""
    bulb = wizlight(ip)
    
    try:
        await bulb.turn_on(PilotBuilder(brightness=level, device=device))
        click.echo(f"✓ Set {ip} brightness to {level}")
    except Exception as e:
        click.echo(f"✗ Error: {e}")
    finally:
        await bulb.async_close()


if __name__ == "__main__":
    main()
