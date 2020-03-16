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
    # default port for WiZ lights
    SCENES = {
                1:"Ocean",
                2:"Romance",
                3:"Sunset",
                4:"Party",
                5:"Fireplace",
                6:"Cozy",
                7:"Forest",
                8:"Pastel Colors",
                9:"Wake up",
                10:"Bedtime",
                11:"Warm White",
                12:"Daylight",
                13:"Cool white",
                14:"Night light",
                15:"Focus",
                16:"Relax",
                17:"True colors",
                18:"TV time",
                19:"Plantgrowth",
                20:"Spring",
                21:"Summer",
                22:"Fall",
                23:"Deepdive",
                24:"Jungle",
                25:"Mojito",
                26:"Club",
                27:"Christmas",
                28:"Halloween",
                29:"Candlelight",
                30:"Golden white",
                31:"Pulse",
                32:"Steampunk"
    }

    def __init__ (self, ip, port=38899):
        ''' Constructor with ip of the bulb '''
        self.ip = ip
        self.port = port
        

    @property
    def warm_white(self) -> int:
        ''' 
            get the value of the warm white led 
        '''
        resp = self.getState()
        if "w" in resp['result']:
            return resp['result']['w']
        else:
            return None

    @warm_white.setter
    def warm_white(self, value: int):
        '''
            set the value of the cold white led
        '''
        if value > 0 and value < 256:
            message = r'{"method":"setPilot","params":{"w":%i}}' % (value)
            self.sendUDPMessage(message)

    @property
    def speed(self) -> int:
        ''' 
            get the color changing speed
        '''
        resp = self.getState()
        if "speed" in resp['result']:
            return resp['result']['speed']
        else:
            return None

    @speed.setter
    def speed(self, value: int):
        '''
            set the color changing speed in precent (0-100)
            This applies only to changing effects!
        '''
        if value > 0 and value < 101:
            message = r'{"method":"setPilot","params":{"speed":%i}}' % (value)
            self.sendUDPMessage(message)
        else:
            raise IndexError("Value must be between 0 and 100")

    @property
    def scene(self) -> str:
        '''
            get the current scene name
        '''
        id = self.getState()['result']['sceneId']
        if id in self.SCENES:
            return self.SCENES[id]
        else:
            return None

    @scene.setter
    def scene(self, scene_id: int):
        '''
            set the scene by id
        '''
        if scene_id in self.SCENES:
            message = '{"method":"setPilot","params":{"sceneId":%i}}' % scene_id
            self.sendUDPMessage(message)
        else:
            # id not in SCENES !
            raise IndexError("Scene is not available - only 0 to 32 are supported")

    @property
    def cold_white(self) -> int:
        '''
            get the value of the cold white led
        '''
        resp = self.getState()
        if "c" in resp['result']:
            return resp['result']['c']
        else:
            return None

    @cold_white.setter
    def cold_white(self, value: int):
        '''
            set the value of the cold white led
        '''
        if value > 0 and value < 256:
            message = r'{"method":"setPilot","params":{"c":%i}}' % (value)
            self.sendUDPMessage(message)
        else:
            raise IndexError("Value must be between 1 and 255")
            
    @property
    def rgb(self):
        '''
            get the rgb color state of the bulb and turns it on
        '''
        resp = self.getState()
        if "r" in resp['result'] and "g" in resp['result'] and "b" in resp['result']:
            r = resp['result']['r']
            g = resp['result']['g']
            b = resp['result']['b']
            return r, g, b
        else:
            # no RGB color value was set
            return None, None, None

    @rgb.setter
    def rgb(self, values):
        '''
            set the rgb color state of the bulb
        '''
        r, g, b = values
        message = r'{"method":"setPilot","params":{"r":%i,"g":%i,"b":%i}}' % (r,g,b)
        self.sendUDPMessage(message)

    @property
    def brightness(self) -> int:
        '''
            gets the value of the brightness 0-255
        '''
        return self.percent_to_hex(self.getState()['result']['dimming'])

    @brightness.setter
    def brightness(self, value: int):
        '''
            set the value of the brightness 0-255
        '''
        percent = self.hex_to_percent(value)
        # lamp doesn't supports lower than 10%
        if percent < 10: percent = 10
        message = r'{"method":"setPilot","params":{"dimming":%i}}' % percent
        self.sendUDPMessage(message)
    
    @property
    def colortemp(self) -> int:
        resp = self.getState()
        if "temp" in resp['result']:
            return resp['result']['temp']
        else:
            return None

    @colortemp.setter
    def colortemp(self, kelvin: int):
        '''
            sets the color temperature for the white led in the bulb
        '''
        # normalize the kelvin values - should be removed
        if kelvin < 2500: kelvin = 2500
        if kelvin > 6500: kelvin = 6500 
        
        message = r'{"method":"setPilot","params":{"temp":%i}}' % kelvin
        self.sendUDPMessage(message)

    @property
    def status(self) -> bool:
        '''
            returns true or false / true = on , false = off
        '''
        resp = self.getState()
        if "state" in resp['result']:
            return resp['result']['state']
        else:
            raise ValueError("Cant read response for 'state' from the bulb. Debug:", resp)

    ## ------------------ Non properties --------------

    def turn_off(self):
        '''
            turns the light off
        '''
        message = r'{"method":"setPilot","params":{"state":false}}'
        self.sendUDPMessage(message)

    def turn_on(self):
        '''
            turns the light on
        '''
        message = r'{"method":"setPilot","params":{"state":true}}'
        self.sendUDPMessage(message)
    
    def get_id_from_scene_name(self, scene: str) -> int: 
        ''' gets the id from a scene name '''
        for id in self.SCENES:
            if self.SCENES[id] == scene:
                return id
        raise ValueError("Scene '%s' not in scene list." % scene)

    ### ---------- Helper Functions ------------
    def getState(self):
        '''
            getPilot - gets the current bulb state - no paramters need to be included
            {"method": "getPilot", "id": 24}
        '''
        message = r'{"method":"getPilot","params":{}}'
        return self.sendUDPMessage(message)

    def getBulbConfig(self):
        '''
            returns the configuration from the bulb
        '''
        message = r'{"method":"getSystemConfig","params":{}}'
        return self.sendUDPMessage(message)
    
    def lightSwitch(self):
        '''
            turns the light bulb on or off like a switch
        '''
        # first get the status
        result = self.getState()
        if result['result']['state']:
            # if the light is on - switch off
            self.turn_off()
        else:
            # if the light is off - turn on
            self.turn_on()
    
    def getConnection(self) -> bool:
        '''
            returns true or false and indicates the connection state
        '''
        try:
            self.getState()
            return True
        except OSError:
            return False


    def sendUDPMessage(self, message):
        '''
            send the udp message to the bulb
        '''
         # fix port for Wiz Lights
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        sock.sendto(bytes(message, "utf-8"), (self.ip, self.port))
        sock.settimeout(20.0)
        data, addr = sock.recvfrom(1024)
        if len(data) is not None:
            resp = json.loads(data.decode())
            if "error" not in resp:
                    return resp
            else:
                # exception should be created
                raise ValueError("Cant read response from the bulb. Debug:",resp)

    def hex_to_percent(self, hex):
        ''' converts hex 0-255 values to percent '''
        return round((hex/255)*100)

    def percent_to_hex(self, percent):
        ''' converts percent values 0-100 into hex 0-255'''
        return round((percent / 100)*255)
    
