# PilotBuilder


Get information from the bulb. 

## Methods


### __init__


Set the parameter. 

#### Parameters
name | description | default
--- | --- | ---
self |  | 
warm_white |  | None
cold_white |  | None
speed |  | None
scene |  | None
rgb |  | None
brightness |  | None
colortemp |  | None





### get_pilot_message


Return the pilot message. 

#### Parameters
name | description | default
--- | --- | ---
self |  | 





### _set_warm_white


Set the value of the cold white led. 

#### Parameters
name | description | default
--- | --- | ---
self |  | 
value |  | 





### _set_cold_white


Set the value of the cold white led. 

#### Parameters
name | description | default
--- | --- | ---
self |  | 
value |  | 





### _set_speed


Set the color changing speed in precent (0-100).   
This applies only to changing effects. 

#### Parameters
name | description | default
--- | --- | ---
self |  | 
value |  | 





### _set_scene


Set the scene by id. 

#### Parameters
name | description | default
--- | --- | ---
self |  | 
scene_id |  | 





### _set_rgb


Set the RGB color state of the bulb. 

#### Parameters
name | description | default
--- | --- | ---
self |  | 
values |  | 





### _set_brightness


Set the value of the brightness 0-255. 

#### Parameters
name | description | default
--- | --- | ---
self |  | 
value |  | 





### _set_colortemp


Set the color temperature for the white led in the bulb. 

#### Parameters
name | description | default
--- | --- | ---
self |  | 
kelvin |  | 





### hex_to_percent


Convert hex 0-255 values to percent. 

#### Parameters
name | description | default
--- | --- | ---
self |  | 
hex |  | 




