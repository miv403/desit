
class Device:
    
    def __init__(self, addr, devID):
        
        self.ADDR = addr
        self.ID = devID
        
    
    def getID(self):
        
        return self.ID