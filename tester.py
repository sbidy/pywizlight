from pywizlight import wizlight


def hex_to_percent(hex):
    return (hex/255)*100

light = wizlight("192.168.178.95")

light.lightSwitch()

light.color = (255, 255, 0, 0)
print(light.color)

light.brightness = hex_to_percent(127)
print(light.brightness)

light.turn_off()