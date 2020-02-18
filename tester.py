import wizconnect 

light = wizconnect.wizlight("192.168.178.95")
#light.setColor(255,255,0,0,50)
#print(light.getPilot())
light.lightSwitch()
#light.setDimmer(100)
#light.setColorTemperature(6500)