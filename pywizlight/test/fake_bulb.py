"""Start up a fake bulb to test features without a real bulb."""
import json
import socketserver
import threading

BULB_INIT_PILOT = json.loads(
    '{\
   "method":"getPilot",\
   "env":"pro",\
   "result":{\
      "mac":"ABCABCABCABC",\
      "rssi":-62,\
      "src":"",\
      "state":false,\
      "sceneId":0,\
      "r":255,\
      "g":127,\
      "b":0,\
      "c":0,\
      "w":0,\
      "temp":0,\
      "dimming":13\
   }\
}\
'
)

BULB_SYS_CONFIG = json.loads(
    '{"method":"getSystemConfig","env":"pro","result":{"mac":"a8bb5006033d","homeId":653906,"roomId":989983,"moduleName"\
    :"","fwVersion":"1.21.0","groupId":0,"drvConf":[20,2],\
    "ewf":[255,0,255,255,0,0,0],"ewfHex":"ff00ffff000000","ping":0}}'
)

BULB_JSON_ERROR = b'{"env":"pro","error":{"code":-32700,"message":"Parse error"}}'


def udp_fake_bulb():
    """Start a fake bulb instance."""

    class BulbUDPRequestHandler(socketserver.DatagramRequestHandler):
        """Class for UDP handler."""

        def handle(self):
            """Handle the request."""
            json_data = None
            data = self.rfile.readline().strip()
            print(f"Reuest:{data}")
            try:
                json_data = json.loads(data.decode())
            except json.JSONDecodeError:
                self.wfile.write(BULB_JSON_ERROR)

            if json_data["method"] == "setPilot":
                return_data = self.setPilot(json_data)
                self.wfile.write(return_data)
            if json_data["method"] == "getPilot":
                print(f"Response:{json.dumps(BULB_INIT_PILOT)}")
                self.wfile.write(bytes(json.dumps(BULB_INIT_PILOT), "utf-8"))
            if json_data["method"] == "getSystemConfig":
                self.wfile.write(bytes(json.dumps(BULB_SYS_CONFIG), "utf-8"))

        def setPilot(self, json_data):
            """Change the values in the state."""
            for name, value in json_data["params"].items():
                BULB_INIT_PILOT["result"][name] = value
                print(f"Change: {json.dumps(BULB_INIT_PILOT)}")
            return b'{"method":"setPilot","env":"pro","result":{"success":true}}'

    UDPServerObject = socketserver.ThreadingUDPServer(
        server_address=("127.0.0.1", 38899), RequestHandlerClass=BulbUDPRequestHandler
    )
    UDPServerObject.daemon_threads = True
    UDPServerObject.serve_forever()


def startup_bulb(module_name="ESP01_SHRGB_03"):
    """Startup the bulb."""
    BULB_SYS_CONFIG["result"]["moduleName"] = module_name
    thread = threading.Thread(target=udp_fake_bulb)
    thread.daemon = True
    thread.start()
