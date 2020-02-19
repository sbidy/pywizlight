from pywizlight import wizlight


def hex_to_percent(hex):
    return (hex/255)*100

light = wizlight("192.168.178.95")

light.turn_on()
light.brightness = 28
print(light.getState())
print(light.brightness)

#light.turn_off()