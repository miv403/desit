import json
from enum import Enum

class MsgType(Enum):
    
    connectionREQ = 0
    connectionOK = 1
    reqPubKey = 2
    repPubKey = 3

class Messaging:
    
    def toDict(self,type,  # enum MsgType
                    addr,  # self.LOCALHOST
                    id ):  # self.ID
        # mesaj ayrıntıları -> dict
        
        msgDict = {"ADDR" : addr,
                    "ID" : id
                }
        if type == MsgType.connectionREQ:
            msgDict["TYPE"] = "CONNECTION::REQ"
        elif type == MsgType.connectionOK:
            msgDict["TYPE"] = "CONNECTION::OK"
        elif type == MsgType.reqPubKey:
            msgDict["TYPE"] = "REQ::PUB_KEY"
        elif type == MsgType.repPubKey:
            msgDict["TYPE"] = "REP::PUB_KEY"

        return msgDict