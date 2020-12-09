# BroadcastProtocol


Protocol that sends an UDP broadcast message for bulb discovery. 

## Methods


### __init__


Init discovery function. 

#### Parameters
name | description | default
--- | --- | ---
self |  | 
loop |  | 
registry |  | 
broadcast_address |  | 





### connection_made


Init connection to socket and register broadcasts. 

#### Parameters
name | description | default
--- | --- | ---
self |  | 
transport |  | 





### broadcast_registration


Send a registration method as UDP broadcast. 

#### Parameters
name | description | default
--- | --- | ---
self |  | 





### datagram_received


Receive data from broadcast. 

#### Parameters
name | description | default
--- | --- | ---
self |  | 
data |  | 
addr |  | 





### connection_lost


Return connection error. 

#### Parameters
name | description | default
--- | --- | ---
self |  | 
exc |  | 




