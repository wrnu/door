from phue import Bridge

class HouseHue():
    def __init__(self, ip):
        self.b = None
        self.ip = ip

    def connect(self):
        try:
            self.b = Bridge(self.ip)
            self.b.connect()
        except:
            pass

    def getFrontDoorState(self):
        try:
            return self.b.get_light('Front Door').get('state')
        except:
            return {'on': False, 'bri': 0}

    def setFrontDoor(self, state, bri):
        try:
            command =  {'transitiontime' : 10, 'on' : state, 'bri' : bri}
            self.b.set_light('Front Door', command)
        except:
            pass
