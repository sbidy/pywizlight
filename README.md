![Upload Python Package](https://github.com/sbidy/pywizlight/workflows/Upload%20Python%20Package/badge.svg)

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-10-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

![Code Quality Check](https://github.com/sbidy/pywizlight/workflows/Lint/badge.svg)
![Update Docs](https://github.com/sbidy/pywizlight/workflows/Update%20Docs/badge.svg)

# pywizlight

A Python connector for WiZ light bulbs.

Tested with the following smart lights:

- [Original Phillips Wiz WiFi LEDs](https://www.lighting.philips.co.in/consumer/smart-wifi-led)
- [SLV Play RGB bulb](https://www.amazon.de/dp/B07PNCDJLW)
- [WiZ Smart LED](https://www.amazon.de/gp/product/B07YLW52MK)

## Install

```bash
pip install pywizlight
```

**Note:** Requires Python version `>=3.7`.

On a Fedora-based system or on a CentOS/RHEL 8 machine which has EPEL enabled, as
[`pywizlight`](https://src.fedoraproject.org/rpms/python-pywizlight) is present in the
Fedora Package Collection.

```bash
sudo dnf -y install python3-pywizlight
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
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## Example

```python
import asyncio

from pywizlight import wizlight, PilotBuilder, discovery

async def main():
    """Sample code to work with bulbs."""
    # Discover all bulbs in the network via broadcast datagram (UDP)
    # function takes the discovery object and returns a list with wizlight objects.
    bulbs = await discovery.find_wizlights()
    # Print the IP address of the bulb on index 0
    print(f"Bulb IP address: {bulbs[0].ip}")

    # Iterate over all returned bulbs
    for bulb in bulbs:
        print(bulb.__dict__)
        # Turn off all available bulbs
        # await bulb.turn_off()

    # Set up a standard light
    light = wizlight("192.168.0.170")
    # Set up the light with a custom port
    #light = wizlight("your bulb's IP address", port=12345)

    # The following calls need to be done inside an asyncio coroutine
    # to run them fron normal synchronous code, you can wrap them with
    # asyncio.run(..).

    # Turn on the light into "rhythm mode"
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
    bulb_type = await bulb.get_bulbtype()
    print(bulb_type.features.brightness) # returns true if brightness is supported
    print(bulb_type.features.color) # returns true if color is supported
    print(bulb_type.features.color_tmp) # returns true if color temperatures are supported
    print(bulb_type.features.effect) # returns true if effects are supported
    print(bulb_type.kelvin_range.max) # returns max kelvin in in INT
    print(bulb_type.kelvin_range.min) # returns min kelvin in in INT
    print(bulb_type.name) # returns the module name of the bulb

    # Turns the light off
    await light.turn_off()

    # Do operations on multiple lights parallely
    #bulb1 = wizlight("<your bulb1 ip>")
    #bulb2 = wizlight("<your bulb2 ip>")
    #await asyncio.gather(bulb1.turn_on(PilotBuilder(brightness = 255)),
    #    bulb2.turn_on(PilotBuilder(warm_white = 255)), loop = loop)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

## CLI

`wizlight` is a command-line tool to perform basic interactions with bulbs.

```bash
$ wizlight
Usage: wizlight [OPTIONS] COMMAND [ARGS]...

  Simple command-line tool to interact with Wizlight bulbs.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  discover  Disocver bulb in the local network.
  off       Turn the bulb off.
  on        Turn the bulb on.
  state     Get the current state from the given bulb.
```

## Discovery

The discovery works with an UDP Broadcast request and collects all bulbs in the network.

## Bulb paramters (UDP RAW)

- **sceneId** - calls one of thr predefined scenes (int from 0 to 32) [List of names in code](https://github.com/sbidy/pywizlight/blob/master/pywizlight/scenes.py)
- **speed** - sets the color changing speed in percent
- **dimming** - sets the dimmer of the bulb in percent
- **temp** - sets color temperature in kelvins
- **r** - red color range 0-255
- **g** - green color range 0-255
- **b** - blue color range 0-255
- **c** - cold white range 0-255
- **w** - warm white range 0-255
- **id** - the bulb id
- **state** - when it's on or off
- **schdPsetId** - rhythm id of the room

## Async I/O

For async I/O this component uses https://github.com/jsbronder/asyncio-dgram, which internally uses asyncio DatagramTransport, which allows completely non-blocking UDP transport

## Classes

`wizlight(ip)`: Creates a instance of a WiZ Light Bulb. Constructed with the IP address of the bulb.

### Instance variables

You need to first fetch the state by calling `light.updateState()`.
After that all state can be fetched from `light.state`, which is a `PilotParser` object.

`PilotParser.get_brightness()`gets the value of the brightness 0-255

`PilotParser.get_rgb()` get the rgbW color state of the bulb

`PilotParser.get_colortemp()` get the color temperature ot the bulb

`PilotParser.get_warm_white/get_cold_white()` get the current warm/cold setting (not supported by original Phillips Wiz bulbs)

`PilotParser.get_scene()` gets the current scene name

`PilotParser.get_state()` returns true or false / true = on , false = off

### Methods

`getBulbConfig(self)` returns the hardware configuration of the bulb

`updateState(self)` gets the current bulb state from the light using `sendUDPMessage` and sets it to `self.state`

`lightSwitch(self)` turns the light bulb on or off like a switch

`getMAC(self)` returns the MAC address of the bulb. Can be used as unique ID.

`sendUDPMessage(self, message, timeout = 60, send_interval = 0.5, max_send_datagrams = 100):` sends the udp message to the bulb. Since UDP can loose packets, and your light might be a long distance away from the router, we continuously keep sending the UDP command datagram until there is a response from the light. This has in tests worked way better than just sending once and just waiting for a timeout. You can set the async operation timeout using `timeout`, the time interval to sleep between continuous UDP sends using `send_interval` and the maximum number of continuous pings to send using `max_send_datagrams`. It is already hard coded to a lower value for `setPilot` (set light state) vs `getPilot` (fetch light state) so as to avoid flickering the light.

`turn_off(self)` turns the light off

`turn_on(PilotBuilder)` turns the light on. This take a `PilotBuilder` object, which can be used to set all the parameters programmatically - rgb, color temperature, brightness, etc. To set the light to rhythm mode, create an empty `PilotBuilder`.

## Bulb methods (UDP native):

- **getSystemConfig** - gets the current system configuration - no parameters need
- **syncPilot** - sent by the bulb as heart-beats
- **getPilot** - gets the current bulb state - no parameters need to be included
- **setPilot** - used to tell the bulb to change color/temp/state
- **Pulse** - uncertain of purpose
- **Registration** - used to "register" with the bulb: This notifies the built that
  it you want it to send you heartbeat sync packets.

### Sync functions:

- syncUserConfig
- syncPilot - {"method":"syncPilot","env":"pro","params":{"mac":"ABCABCABC","rssi":-71,"src":"udp","state":true,"sceneId":0,"temp":6500,"dimming":62}}
- syncSchdPset
- syncBroadcastPilot
- syncSystemConfig
- syncConfig
- syncAlarm

### Set functions:

- pulse - {"method":"pulse", {"params":{"delta":-15,"duration":300}}
- registration - {"method":"registration","id":105,{"params":{"phoneIp":"10.0.0.0","phoneMac":"aaaaaaaaaaaa","register":true}}
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
