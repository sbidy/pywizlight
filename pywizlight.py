'''
     MIT License

     Copyright (c) 2020 Stephan Traub

     Permission is hereby granted, free of charge, to any person obtaining a copy
     of this software and associated documentation files (the "Software"), to deal
     in the Software without restriction, including without limitation the rights
     to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     copies of the Software, and to permit persons to whom the Software is
     furnished to do so, subject to the following conditions:

     The above copyright notice and this permission notice shall be included in all
     copies or substantial portions of the Software.

     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
     SOFTWARE.
'''
import socket
import json

class wizlight:
    '''
        Creates a instance of a WiZ Light Bulb
    '''
    def __init__ (self, ip):
        ''' Constructor with ip of the bulb '''
        self.ip = ip

    @color.setter
    def color(self, r=0, g=0, b=0, w=0):
        ''' set the rgbw color state of the bulb '''
        message = r'{"method":"setPilot","params":{"r":%i,\
                                                    "g":%i,\
                                                    "b":%i,\
                                                    "w":%i}}' % (r,g,b,w)
        self.sendUDPMessage(message)

    @property
    def color(self):
        ''' get the rgb color state of the bulb '''
        repose = self.getState()
        if "temp" not in repose:
            r = repose['result']['r']
            g = repose['result']['g']
            b = repose['result']['b']
            w = repose['result']['w']
            return r, g, b, w
        else:
            # no RGB color value was set
            return None, None, None

    @brightness.setter
    def brightness(self, percent=100):
        ''' set the precentage of the dimming value 0-100% '''
        message = r'{"method":"setPilot","params":{"dimming":%i}}' % percent
        self.sendUDPMessage(message)
    
    @property
    def brightness(self):
        ''' gets the precentage of the dimming value 0-100% '''
        return self.getState()['result']['dimming']

    @colortemp.setter
    def colortemp(self, kelvin):
        ''' sets the color temperature for the white led in the bulb '''
        if kelvin > 2499 and kelvin < 6501:
            message = r'{"method":"setPilot","params":{"temp":%i}}' % kelvin
            self.sendUDPMessage(message)
        else:
            raise ValueError("Value out of range. The value for kelvin must be between 2500 and 6500")
    
    @property
    def colortemp(self):
        repose = self.getState()
        if "temp" in repose:
            return repose['result']['temp']
        else:
            return None
    
    def getState(self):
        '''
        getPilot - gets the current bulb state - no paramters need to be included
        {"method": "getPilot", "id": 24}
        '''
        message = r'{"method":"getPilot","params":{}}'
        return self.sendUDPMessage(message)

    def getBulbConfig(self):
        ''' returns the configuration from the bulb '''
        message = r'{"method":"getSystemConfig","params":{}}'
        return self.sendUDPMessage(message)
    

    def lightSwitch(self):
        '''
        turns the light bulb on or off
        '''
        # first get the status
        message = r'{"method":"getPilot","params":{}}'
        result = self.sendUDPMessage(message)
        if result['result']['state']:
            # if the light is on - switch off
            message = r'{"method":"setPilot","params":{"state":false}}'
        else:
            # if the light is off - turn on
            message = r'{"method":"setPilot","params":{"state":true}}'
        self.sendUDPMessage(message)

    def sendUDPMessage(self, message):
        ''' send the udp message to the bulb '''
        UDP_PORT = 38899 # fix port for Wiz Lights
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        sock.sendto(bytes(message, "utf-8"), (self.ip, UDP_PORT))
        sock.settimeout(30.0)
        data, addr = sock.recvfrom(1024)
        if len(data) is not None:
            resp = json.loads(data.decode())
            if "error" not in resp:
                    return resp
            else:
                # exception should be created
                raise ValueError(resp)