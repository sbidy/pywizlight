# Python Documentation

## Classes

**[Features](Features.md)**: Defines the supported features. 

**[KelvinRange](KelvinRange.md)**: Deines the kelvin range. 

**[BulbType](BulbType.md)**: BulbType object to define functions and features of the bulb. 

**[BulbLib](BulbLib.md)**: Provides all existing bulbs. 

**[DiscoveredBulb](DiscoveredBulb.md)**: Representation of discovered bulb. 

**[BulbRegistry](BulbRegistry.md)**: Representation of the bulb registry. 

**[BroadcastProtocol](BroadcastProtocol.md)**: Protocol that sends an UDP broadcast message for bulb discovery. 

**[WizLightError](WizLightError.md)**: General WizLightError exception occurred. 

**[WizLightConnectionError](WizLightConnectionError.md)**: When a connection error is encountered. 

**[WizLightTimeOutError](WizLightTimeOutError.md)**: When a connection error is encountered. 

**[WizLightNotKnownBulb](WizLightNotKnownBulb.md)**: The bulb type is not known to the pywizlight. 

**[PilotBuilder](PilotBuilder.md)**: Get information from the bulb. 

**[PilotParser](PilotParser.md)**: Interpret the message from the bulb. 

**[wizlight](wizlight.md)**: Create an instance of a WiZ Light Bulb. 

**[TestBulb](TestBulb.md)**: Bulb test class. 


## Functions

### get_version


Define the version number. 




### coro


Allow to use async in click. 
#### Parameters
name | description | default
--- | --- | ---
f |  | 





### main


Command-line tool to interact with Wizlight bulbs. 




### udp_fake_bulb


Start a fake bulb instance. 




### startup_bulb


Start up the bulb. 
#### Parameters
name | description | default
--- | --- | ---
module_name |  | "ESP01_SHRGB_03"




