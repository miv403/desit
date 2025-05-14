import zmq

from services import ServiceDiscover
from messaging import Messaging, MsgType

class Device:

    def __init__(self,
                id_,                # self.ID
                hostName,           # Host.HOSTNAME
                hostID,             # Host.ID
                hostPubKey,         # Host.PUB_KEY
                devPubKey = None):  # self.PUB_KEY

        self.ID = id_
        # self.ADDR = self.discoverAddr()
        self.ADDR = None
        
        self.messaging = Messaging(
            hostName = hostName,
            hostID = hostID,
            devID = self.ID,
            pubKey = hostPubKey
        )
        
        if not devPubKey:
            PUB_KEY = self.req(self.messaging.toDict(MsgType.reqPubKey)) # DONE test: req()
            if not PUB_KEY:
                self.PUB_KEY = None
                return

            self.PUB_KEY =  self.PUB_KEY['PUB_KEY']
        else:
            self.PUB_KEY = devPubKey

    def getID(self):
        return self.ID
    def getAddr(self):
        return self.ADDR
    def getPubKey(self):
        return self.PUB_KEY

    def discoverAddr(self):
        # ID ile IP adresi keşfi
        
        sd = ServiceDiscover(self.ID)
        addr = sd.discover()

        if not addr:
            print(f"[DEVICE] {self.ID} is offline")
        return addr

    def req(self, msgDict) -> dict:
        # DONE msg type metot kullanıcısı tarafından belirlenecek
        
        # güncel adresi al
        self.ADDR = self.discoverAddr()
        
        if not self.ADDR: # aygıt çevrim dışı ise isteği gerçekleştirme
            print(f"[REQ] {self.ID} is offline")
            return None
        
        context = zmq.Context()
        print(f"[REQ] Requesting from {self.ADDR} ID: {self.ID}")
        socket = context.socket(zmq.REQ)
        socket.connect(f"tcp://{self.ADDR}:6162") # DONE REP-REQ portu belirle

        socket.send_json(msgDict)
        
        message = socket.recv_json()
        
        print(f"[REQ] Received reply from {self.ADDR}: {message}")
        
        return message
