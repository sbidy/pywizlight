import socket
import json

class wizlight:
    '''
        Creates a instance of a WiZ Light Bulb

        Bulb methodes:
            getSystemConfig - gets the current system configuration - no paramters need
            syncPilot - sent by the bulb as heart-beats
            getPilot - gets the current bulb state - no paramters need to be included
            setPilot - used to tell the bulb to change color/temp/state
            Pulse - uncertain of purpose
            Registration - used to "register" with the bulb: This notifies the built that
                            it you want it to send you heartbeat sync packets.
        Bulb paramters:
            sceneId - calls one of thr predefined scenes (int from 0 to 12?)
            speed - sets the color changing speed in precent
            dimming - sets the dimmer of the bulb in precent
            r - red color range 0-255
            g - green color range 0-255
            b - blue color range 0-255
            c - ????
            w - white color range 0-255
            id - the bulb id

    '''
    def __init__ (self, ip):
        ''' Constructor with ip of the bulb '''
        self.ip = ip

    def setColor(self, r=0, g=0, b=0, w=0):
        ''' used to tell the bulb to change color/temp/state '''
        message = r'{"method":"setPilot","params":{"r":%i,\
                                                    "g":%i,\
                                                    "b":%i,\
                                                    "w":%i}}' % (r,g,b,w)
        self.sendUDPMessage(message)

    def setDimmer(self, percent=100):
        ''' set the precentage of the dimming value 0-100% '''
        message = r'{"method":"setPilot","params":{"dimming":%i}}' % percent
        self.sendUDPMessage(message)

    def setColorTemperature(self, kelvin):
        ''' sets the color temperature for the white led in the bulb '''
        if kelvin > 2499 and kelvin < 6501:
            message = r'{"method":"setPilot","params":{"temp":%i}}' % kelvin
            self.sendUDPMessage(message)
        else:
            raise ValueError("Value out of range. The value for kelvin must be between 2500 and 6500")

    def getState(self):
        '''
        getPilot - gets the current bulb state - no paramters need to be included
        {"method": "getPilot", "id": 24}
        '''
        message = r'{"method":"getPilot","params":{}}'
        return self.sendUDPMessage(message)

    def lightSwitch(self):
        '''
        turns the light bulb on or off
        '''
        # first get the status
        message = r'{"method":"getPilot","params":{}}'
        result = self.sendUDPMessage(message)
        print(result)
        if result['result']['state']:
            # it the light is on - switch off
            message = r'{"method":"setPilot","params":{"state":false}}'
        else:
            # if the light is off - turn on
            message = r'{"method":"setPilot","params":{"state":true}}'
        self.sendUDPMessage(message)

    def sendUDPMessage(self, message):
        ''' send the udp message to the light '''
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