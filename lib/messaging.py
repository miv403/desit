from enum import Enum
from lib.constants import Const

class MsgType(Enum):
    
    hello = 0
    reqPubKey = 1   # REQ::PUB_KEY
    repPubKey = 2   # REP::PUB_KEY
    disconnect = 3

class Messaging:
    
    def __init__(self,  # hostName = None, # Host.HOSTNAME
                        hostID = None,  # Host.ID
                        devID = None,   # Device.ID
                        pubKey = None): # Host.PUB_KEY

        # self.HOSTNAME = hostName
        self.HOST_ID = hostID
        self.DEV_ID = devID
        self.PUB_KEY = pubKey # hostPubKey
    
    def toDict(self,
                type): # enum MsgType  
        # mesaj ayrıntıları -> dict
        
        msgDict = {
                    "TYPE" : None,
                    "TO" : self.DEV_ID,
                    "FROM" : self.HOST_ID,
                    "HOSTNAME" : Const.HOSTNAME,
                    "USERNAME" : Const.USERNAME,
                    "PUB_KEY" : self.PUB_KEY
                }

        if type == MsgType.hello:
            msgDict['TYPE'] = "HELLO"
        elif type == MsgType.reqPubKey:
            msgDict['TYPE'] = "REQ::PUB_KEY"
        elif type == MsgType.repPubKey:
            msgDict['TYPE'] = "REP::PUB_KEY"

        return msgDict
