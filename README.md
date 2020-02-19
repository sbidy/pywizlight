# pywizlight
A python connector for WiZ light bulbs.
Work in progress an only tested with the [SLV Play RGB bulb](https://www.amazon.de/dp/B07PNCDJLW).


## Bulb methodes:
  getSystemConfig - gets the current system configuration - no paramters need
  syncPilot - sent by the bulb as heart-beats
  getPilot - gets the current bulb state - no paramters need to be included
  setPilot - used to tell the bulb to change color/temp/state
  Pulse - uncertain of purpose
  Registration - used to "register" with the bulb: This notifies the built that
                            it you want it to send you heartbeat sync packets.
## Bulb paramters:
  sceneId - calls one of thr predefined scenes (int from 0 to 12?)
  speed - sets the color changing speed in precent
  dimming - sets the dimmer of the bulb in precent
  r - red color range 0-255
  g - green color range 0-255
  b - blue color range 0-255
  c - ????
  w - white color range 0-255
  id - the bulb id
