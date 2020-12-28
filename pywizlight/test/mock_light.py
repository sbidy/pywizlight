"""
Mock for the Bulb API.

{"method":"getPilot","params":{}} = {"method":"getPilot","env":"pro","result":{"mac":"a8bb5006033d","rssi":-62,"src":"","state":false,"sceneId":0,"r":255,"g":127,"b":0,"c":0,"w":0,"dimming":13}}
{"method":"{"method": "setPilot", "params":{"dimming":12}}","params":{}} = {"method":"getSystemConfig","env":"pro","result":{"mac":"a8bb5006033d","homeId":653906,"roomId":989983,"moduleName":"ESP01_SHRGB_03","fwVersion":"1.21.0","groupId":0,"drvConf":[20,2],"ewf":[255,0,255,255,0,0,0],"ewfHex":"ff00ffff000000","ping":0}}
{"method": "setPilot", "params":{dimming:"12"}
Wrong value = {"env":"pro","error":{"code":-32700,"message":"Parse error"}}
{"method": "setPilot", "params":{"dimming":12}}
"""


def getSystemConfig():
    """Retruns the system config."""
    return '{"method":"getSystemConfig","env":"pro","result": \
    {"mac":"ABCABCABCABC","homeId":653906,"roomId":989983,"moduleName":"ESP01_SHRGB_03",\
    "fwVersion":"1.21.0","groupId":0,"drvConf":[20,2],"ewf":[255,0,255,255,0,0,0],"ewfHex":"ff00ffff000000","ping":0}}'
