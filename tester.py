from pywizlight import wizlight
import time

light = wizlight("192.168.178.98")

light.turn_on()
print(light.getState())
## test part
light.warm_white = 255
print(light.warm_white)
#light.cold_white = 255
print(light.cold_white)

## emd test
print(light.getState())
time.sleep(4)
light.turn_off()