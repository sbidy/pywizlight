![Upload Python Package](https://github.com/sbidy/pywizlight/workflows/Upload%20Python%20Package/badge.svg)

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-18-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

![Update Docs](https://github.com/sbidy/pywizlight/workflows/Update%20Docs/badge.svg)
[![Lint](https://github.com/sbidy/pywizlight/actions/workflows/lint.yml/badge.svg)](https://github.com/sbidy/pywizlight/actions/workflows/lint.yml)
[![codecov][code-cover-shield]][code-coverage]


# pywizlight

A Python connector for [WiZ](https://www.wizconnected.com/en/consumer/) devices.

# Wiz Ligt API Documentation

https://docs.pro.wizconnected.com/#introduction

## Install

```bash
pip install pywizlight
```

**Note:** Requires Python version `>=3.7`.

### Fedora/CentOS

On a Fedora-based system or on a CentOS/RHEL 8 machine which has EPEL enabled, as
[`pywizlight`](https://src.fedoraproject.org/rpms/python-pywizlight) is present in the
Fedora Package Collection.

```bash
sudo dnf -y install python3-pywizlight
```

### NixOS

For NixOS and Nix the latest release of `pywizlight` is usually available in the [`unstable`](https://search.nixos.org/packages?channel=unstable&query=pywizlight)
channel. Stable releases might ship older versions of `pywizlight`.

```bash
nix-env -iA nixos.python37Packages.pywizlight
```

## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="http://mtnspring.org"><img src="https://avatars.githubusercontent.com/u/223277?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Seth Nickell</b></sub></a><br /><a href="https://github.com/sbidy/pywizlight/commits?author=snickell" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/daanzu"><img src="https://avatars.githubusercontent.com/u/4319503?v=4?s=100" width="100px;" alt=""/><br /><sub><b>David Zurow</b></sub></a><br /><a href="https://github.com/sbidy/pywizlight/commits?author=daanzu" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/eibanez"><img src="https://avatars.githubusercontent.com/u/438494?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Eduardo Ibanez</b></sub></a><br /><a href="https://github.com/sbidy/pywizlight/commits?author=eibanez" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/angadsingh"><img src="https://avatars.githubusercontent.com/u/1623026?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Angad Singh</b></sub></a><br /><a href="https://github.com/sbidy/pywizlight/commits?author=angadsingh" title="Code">💻</a></td>
    <td align="center"><a href="http://fabian-affolter.ch/blog/"><img src="https://avatars.githubusercontent.com/u/116184?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Fabian Affolter</b></sub></a><br /><a href="https://github.com/sbidy/pywizlight/commits?author=fabaff" title="Documentation">📖</a> <a href="https://github.com/sbidy/pywizlight/commits?author=fabaff" title="Code">💻</a></td>
    <td align="center"><a href="https://redaxmedia.com"><img src="https://avatars.githubusercontent.com/u/1835397?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Henry Ruhs</b></sub></a><br /><a href="https://github.com/sbidy/pywizlight/commits?author=redaxmedia" title="Code">💻</a></td>
    <td align="center"><a href="https://www.panu.it/"><img src="https://avatars.githubusercontent.com/u/2248402?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Alberto Panu</b></sub></a><br /><a href="https://github.com/sbidy/pywizlight/commits?author=bigjohnson" title="Code">💻</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/skitterrusty"><img src="https://avatars.githubusercontent.com/u/71942600?v=4?s=100" width="100px;" alt=""/><br /><sub><b>skitterrusty</b></sub></a><br /><a href="https://github.com/sbidy/pywizlight/commits?author=skitterrusty" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/mots"><img src="https://avatars.githubusercontent.com/u/26517?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Mathias Roth</b></sub></a><br /><a href="https://github.com/sbidy/pywizlight/commits?author=mots" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/durnezj"><img src="https://avatars.githubusercontent.com/u/11504333?v=4?s=100" width="100px;" alt=""/><br /><sub><b>durnezj</b></sub></a><br /><a href="https://github.com/sbidy/pywizlight/commits?author=durnezj" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/Dirty-No"><img src="https://avatars.githubusercontent.com/u/54525684?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Noëlle</b></sub></a><br /><a href="https://github.com/sbidy/pywizlight/commits?author=Dirty-No" title="Documentation">📖</a></td>
    <td align="center"><a href="https://linkedin.com/in/scriptsrc"><img src="https://avatars.githubusercontent.com/u/8009126?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Patrick Kelley</b></sub></a><br /><a href="https://github.com/sbidy/pywizlight/commits?author=scriptsrc" title="Documentation">📖</a></td>
    <td align="center"><a href="http://ellismichael.com"><img src="https://avatars.githubusercontent.com/u/1312141?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Ellis Michael</b></sub></a><br /><a href="https://github.com/sbidy/pywizlight/commits?author=emichael" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/SvbZ3r0"><img src="https://avatars.githubusercontent.com/u/57280279?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Gughan Ravikumar</b></sub></a><br /><a href="https://github.com/sbidy/pywizlight/commits?author=SvbZ3r0" title="Code">💻</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/CharlotteCross1998"><img src="https://avatars.githubusercontent.com/u/29734551?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Charlotte</b></sub></a><br /><a href="https://github.com/sbidy/pywizlight/commits?author=CharlotteCross1998" title="Code">💻</a></td>
    <td align="center"><a href="https://akx.github.io/"><img src="https://avatars.githubusercontent.com/u/58669?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Aarni Koskela</b></sub></a><br /><a href="https://github.com/sbidy/pywizlight/commits?author=akx" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/UH-60"><img src="https://avatars.githubusercontent.com/u/4968133?v=4?s=100" width="100px;" alt=""/><br /><sub><b>UH-60</b></sub></a><br /><a href="https://github.com/sbidy/pywizlight/commits?author=UH-60" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/bdraco"><img src="https://avatars.githubusercontent.com/u/663432?v=4?s=100" width="100px;" alt=""/><br /><sub><b>J. Nick Koston</b></sub></a><br /><a href="https://github.com/sbidy/pywizlight/commits?author=bdraco" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## Discover bulbs via CLI

To find bulbs via cli you can use the following:
```bash
python -m pywizlight.cli discover
```

## Example

```python
import asyncio

from pywizlight import wizlight, PilotBuilder, discovery

async def main():
    """Sample code to work with bulbs."""
    # Discover all bulbs in the network via broadcast datagram (UDP)
    # function takes the discovery object and returns a list of wizlight objects.
    bulbs = await discovery.discover_lights(broadcast_space="192.168.1.255")
    # Print the IP address of the bulb on index 0
    print(f"Bulb IP address: {bulbs[0].ip}")

    # Iterate over all returned bulbs
    for bulb in bulbs:
        print(bulb.__dict__)
        # Turn off all available bulbs
        # await bulb.turn_off()

    # Set up a standard light
    light = wizlight("192.168.1.27")
    # Set up the light with a custom port
    #light = wizlight("your bulb's IP address", port=12345)

    # The following calls need to be done inside an asyncio coroutine
    # to run them from normal synchronous code, you can wrap them with
    # asyncio.run(..).

    # Turn the light on into "rhythm mode"
    await light.turn_on(PilotBuilder())
    # Set bulb brightness
    await light.turn_on(PilotBuilder(brightness = 255))

    # Set bulb brightness (with async timeout)
    timeout = 10
    await asyncio.wait_for(light.turn_on(PilotBuilder(brightness = 255)), timeout)

    # Set bulb to warm white
    await light.turn_on(PilotBuilder(warm_white = 255))

    # Set RGB values
    # red to 0 = 0%, green to 128 = 50%, blue to 255 = 100%
    await light.turn_on(PilotBuilder(rgb = (0, 128, 255)))

    # Get the current color temperature, RGB values
    state = await light.updateState()
    print(state.get_colortemp())
    red, green, blue = state.get_rgb()
    print(f"red {red}, green {green}, blue {blue}")

    # Start a scene
    await light.turn_on(PilotBuilder(scene = 4)) # party

    # Get the name of the current scene
    state = await light.updateState()
    print(state.get_scene())

    # Get the features of the bulb
    bulb_type = await bulbs[0].get_bulbtype()
    print(bulb_type.features.brightness) # returns True if brightness is supported
    print(bulb_type.features.color) # returns True if color is supported
    print(bulb_type.features.color_tmp) # returns True if color temperatures are supported
    print(bulb_type.features.effect) # returns True if effects are supported
    print(bulb_type.kelvin_range.max) # returns max kelvin in INT
    print(bulb_type.kelvin_range.min) # returns min kelvin in INT
    print(bulb_type.name) # returns the module name of the bulb

    # Turn the light off
    await light.turn_off()

    # Do operations on multiple lights in parallel
    #bulb1 = wizlight("<your bulb1 ip>")
    #bulb2 = wizlight("<your bulb2 ip>")
    # --- DEPRECATED in 3.10 see [#140](https://github.com/sbidy/pywizlight/issues/140)
    # await asyncio.gather(bulb1.turn_on(PilotBuilder(brightness = 255)),
    #    bulb2.turn_on(PilotBuilder(warm_white = 255)))
    # --- For >3.10 await asyncio.gather() from another coroutine
    # async def turn_bulbs_on(bulb1, bulb2):
    #    await asyncio.gather(bulb1.turn_on(PilotBuilder(warm_white=255)), bulb2.turn_on(PilotBuilder(warm_white=255)))
    #  def main:
    #    asyncio.run(async turn_bulbs_on(bulb1, bulb2))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

## CLI

`wizlight` is a command-line tool to perform basic interactions with bulbs.

```console
$ wizlight
Usage: wizlight [OPTIONS] COMMAND [ARGS]...

  Simple command-line tool to interact with Wizlight bulbs.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  discover   Discover bulb in the local network.
  off        Turn the bulb off.
  on         Turn the bulb on.
  set-state  Set the current state of a given bulb.
  state      Get the current state from the given bulb.
```

### Examples

```
$ wizlight discover --b 192.168.0.101
Search for bulbs in 192.168.0.101 ...
{'ip_address': '192.168.0.101', 'mac_address': 'a8bs4090193d'}

$ wizlight on --ip 192.168.0.101 --k 3000 --brightness 128
Turning on 192.168.0.101

$ wizlight off --ip 192.168.0.101
Turning off 192.168.0.101

$ wizlight state --ip 192.168.0.101
{'mac': 'a8bs4090193d', 'rssi': -57, 'src': '', 'state': False, 'sceneId': 0, 'temp': 3000, 'dimming': 50}
```

Run `wizlight COMMAND --help` to see usage and options.

## Discovery

The discovery works with a UDP Broadcast request and collects all bulbs in the network.

## Bulb paramters (UDP RAW)

- **sceneId** - calls one of the predefined scenes (int from 1 to 35) [List of names in code](https://github.com/sbidy/pywizlight/blob/master/pywizlight/scenes.py)
- **speed** - sets the color changing speed in percent
- **dimming** - sets the dimmer of the bulb in percent
- **temp** - sets the color temperature in kelvins
- **r** - red color range 0-255
- **g** - green color range 0-255
- **b** - blue color range 0-255
- **c** - cold white range 0-255
- **w** - warm white range 0-255
- **id** - the bulb id
- **state** - whether it's on or off
- **schdPsetId** - rhythm id of the room

## Async I/O

For async I/O this component uses Python's built-in asyncio DatagramTransport, which allows completely non-blocking UDP transport.

## Classes

`wizlight(ip)`: Creates an instance of a WiZ Light Bulb. Constructed with the IP addCancel changesress of the bulb.

### Instance variables

First you need to fetch the state by calling `light.updateState()`.
After that all states can be fetched from `light.state`, which is a `PilotParser` object.

`PilotParser.get_brightness()`gets the value of the brightness 0-255

`PilotParser.get_rgb()` gets the rgbW color state of the bulb

`PilotParser.get_colortemp()` gets the color temperature of the bulb

`PilotParser.get_warm_white/get_cold_white()` gets the current warm/cold setting (not supported by original Philips Wiz bulbs)

`PilotParser.get_scene()` gets the current scene name

`PilotParser.get_state()` returns True/False. True = on, False = off

### Methods

`getBulbConfig(self)` returns the hardware configuration of the bulb

`updateState(self)` gets the current bulb state from the light using `sendUDPMessage` and sets it to `self.state`

`lightSwitch(self)` toggles the light bulb on or off like a switch

`getMAC(self)` returns the MAC address of the bulb. Can be used as a unique ID

`sendUDPMessage(self, message, timeout = 60, send_interval = 0.5, max_send_datagrams = 100):` sends the UDP message to the bulb. Since UDP can lose packets, and your light might be a long distance away from the router, we continuously keep sending the UDP command datagram until there is a response from the bulb. In tests this worked way better than just sending once and waiting for a timeout. You can set the async operation timeout using `timeout`, set the time interval to sleep between continuous UDP sends using `send_interval` and the maximum number of continuous pings to send using `max_send_datagrams`. It is already hardcoded to a lower value for `setPilot` (set light state) vs `getPilot` (fetch light state) to avoid flickering the light.

`turn_off(self)` turns the light off

`turn_on(PilotBuilder)` turns the light on. This takes a `PilotBuilder` object, which can be used to set all the parameters programmatically - rgb, color temperature, brightness, etc. To set the light to rhythm mode, create an empty `PilotBuilder`.

`get_power(self)` returns the current power consumption of a Smart Plug with Metering.

## Bulb methods (UDP native):

- **getSystemConfig** - gets the current system configuration - no parameters required
- **syncPilot** - sent by the bulb as heartbeats
- **getPilot** - gets the current bulb state - no parameters required
- **setPilot** - used to tell the bulb to change color/temp/state
- **Pulse** - uncertain of purpose
- **Registration** - used to "register" with the bulb: This notifies the bulb if you want it to send you heartbeat sync packets

### Sync functions:

- syncUserConfig
- syncPilot - {"method":"syncPilot","env":"pro","params":{"mac":"ABCABCABC","rssi":-71,"src":"udp","state":true,"sceneId":0,"temp":6500,"dimming":62}}
- syncSchdPset
- syncBroadcastPilot
- syncSystemConfig
- syncConfig
- syncAlarm

### Set functions:

- pulse - {"method":"pulse", "params":{"delta":-15,"duration":300}}
- registration - {"method":"registration","id":105, "params":{"phoneIp":"10.0.0.0","phoneMac":"aaaaaaaaaaaa","register":true}}
- setUserConfig
- setSystemConfig
- setDevInfo
- setSchd
- setSchdPset
- setWifiConfig
- reset
- setFavs
- setState
- setPilot

### Get functions

- getPilot
- getUserConfig
- getSystemConfig
- getWifiConfig
- reboot
- getDevInfo

### Error States and Returns

- Parse error
- Invalid Request
- Method not found
- Invalid params
- Internal error
- Success

## Example UDP requests

Send message to the bulb:
`{"method":"setPilot","params":{"r":255,"g":255,"b":255,"dimming":50}}`
Response: `{"method":"setPilot","env":"pro","result":{"success":true}}`

Get state of the bulb:
`{"method":"getPilot","params":{}}`
Responses:

custom color mode:

`{'method': 'getPilot', 'env': 'pro', 'result': {'mac': 'a8bb50a4f94d', 'rssi': -60, 'src': '', 'state': True, 'sceneId': 0, 'temp': 5075, 'dimming': 47}}`

scene mode:

`{'method': 'getPilot', 'env': 'pro', 'result': {'mac': 'a8bb50a4f94d', 'rssi': -65, 'src': '', 'state': True, 'sceneId': 12, 'speed': 100, 'temp': 4200, 'dimming': 47}}`

rhythm mode:

`{'method': 'getPilot', 'env': 'pro', 'result': {'mac': 'a8bb50a4f94d', 'rssi': -63, 'src': '', 'state': True, 'sceneId': 14, 'speed': 100, 'dimming': 100, 'schdPsetId': 9}}`

[code-coverage]: https://codecov.io/gh/sbidy/pywizlight
[code-cover-shield]: https://codecov.io/gh/sbidy/pywizlight/branch/master/graph/badge.svg
