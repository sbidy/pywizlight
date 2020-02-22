from pywizlight import wizlight

light = wizlight("192.168.178.95")

light.turn_on()
print(light.getState())

light.scene = 27
print(light.scene)
print(light.getState())

light.turn_off()