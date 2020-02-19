import pywizlight 

light = pywizlight.wizlight("192.168.178.95")

light.lightSwitch()

#light.setColor(255, 255, 0, 0)
#print(light.getColor)

#light.setColortemp(3000)
print(light.getColortemp)

light.setBrightness(50)
print(light.getBrightness)

#light.turn_off()
print(light.status)

#light.turn_on()
print(light.status)
