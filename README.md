# pywizlight
A python connector for WiZ light bulbs.
Work in progress an only tested with the [SLV Play RGB bulb](https://www.amazon.de/dp/B07PNCDJLW).

## Example
```python
    from pywizlight import wizlight
    # setup a standard light
    light = wizlight("<your bulb ip")
    # setup the light with a custom port
    light = wizlight("<your bulb ip",12345)
     # turn on the light
    light.turn_on()
    # set bulb to warm white color
    light.warm_white = 255
    # print the value 
    print(light.warm_white)
    # set red to 255 = 100%
    light.rgb = 255, 0, 0
    # set green to 255 = 100%
    light.rgb = 0, 255, 0
    # set blue to 255 = 100%
    light.rgb = 0, 0, 255
    # get the current values
    r, g, b = light.rgb
    print("red %i green %i blue %i" % (r, g, b))
    # start a scene 
    light.scene = 14 # party
    # get the name of the current scene
    print(light.scene)
    # set brightness to 255 = 100%
    light.brightness = 255
    # turns the light off
    light.turn_off()

```

## Bulb paramters (UDP RAW):
- **sceneId** - calls one of thr predefined scenes (int from 0 to 32) [Wiki](https://github.com/sbidy/pywizlight/wiki/Light-Scenes)
- **speed** - sets the color changing speed in precent
- **dimming** - sets the dimmer of the bulb in precent
- **r** - red color range 0-255
- **g** - green color range 0-255
- **b** - blue color range 0-255
- **c** - cold white range 0-255
- **w** - warm white range 0-255
- **id** - the bulb id

## Classes

`wizlight(ip)` Creates a instance of a WiZ Light Bulb. Constructor with ip of the bulb

### Instance variables
`brightness`gets the value of the brightness 0-255

`color` get the rgbW color state of the bulb and turns it on

`colortemp` get the color temperature ot the bulb

`rgb` get the rgb color state of the bulb and turns it on

`status` returns true or false / true = on , false = off

### Methods
`getBulbConfig(self)` returns the configuration from the bulb

`getState(self)` gets the current bulb state - no paramters need to be included

`hex_to_percent(self, hex)` helper for convertring 0-255 to 0-100

`percent_to_hex(self, percent)` helper for converting 0-100 into 0-255

`lightSwitch(self)` turns the light bulb on or off like a switch

`sendUDPMessage(self, message)` send the udp message to the bulb

`turn_off(self)` turns the light off

`turn_on(self)` turns the light on

## Bulb methodes (UDP nativ):
- **getSystemConfig** - gets the current system configuration - no paramters need
- **syncPilot** - sent by the bulb as heart-beats
- **getPilot** - gets the current bulb state - no paramters need to be included
- **setPilot** - used to tell the bulb to change color/temp/state
- **Pulse** - uncertain of purpose
- **Registration** - used to "register" with the bulb: This notifies the built that
                            it you want it to send you heartbeat sync packets.

## Example requests
Send message to the bulb:
    `{"method":"setPilot","params":{"r":255,"g":255,"b":255,"dimming":50}}`
Response: `{"method":"setPilot","env":"pro","result":{"success":true}}`

Get state of the bulb:
    `{"method":"getPilot","params":{}}`
Response: `{"method":"getPilot","env":"pro","result":{"mac":"0000000000","rssi":-65,"src":"","state":false,"sceneId":0,"temp":6500,"dimming":100}}`
