from pywizlight import wizlight


def hex_to_percent(hex):
    return (hex/255)*100

light = wizlight("192.168.178.95")

#light.lightSwitch()

light.rgb = (255, 255, 0)
print(light.rgb)

light.turn_off()