# wizlight


Create an instance of a WiZ Light Bulb. 

## Methods


### __init__


Create instance with the IP address of the bulb. 

#### Parameters
name | description | default
--- | --- | ---
self |  | 
ip |  | 
port |  | 38899
mac |  | None





### status


Return the status of the bulb: true = on, false = off. 

#### Parameters
name | description | default
--- | --- | ---
self |  | 





### get_id_from_scene_name


Retrun the id of an given scene name.   
:param scene: Name of the scene :type scene: str :raises ValueError: Retrun if not in scene list :return: ID of the scene :rtype: int 

#### Parameters
name | description | default
--- | --- | ---
self |  | 
scene |  | 




