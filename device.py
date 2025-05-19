import zmq

from services import ServiceDiscover
from messaging import Messaging, MsgType
from constants import Const

class Device:

    def __init__(self,
                id_,                # self.ID
                hostID,             # Host.ID
                hostPubKey,         # Host.PUB_KEY
                devPubKey = None,
                username = None):  # self.PUB_KEY

        self.ID = id_
        # self.ADDR = self.discoverAddr()
        self.ADDR = None
        
        
        self.messaging = Messaging(
            # hostName = hostName,
            hostID = hostID,
            devID = self.ID,
            pubKey = hostPubKey
        )
        
        if not devPubKey:
            request = self.req(self.messaging.toDict(MsgType.reqPubKey)) # DONE test: req()
            if not request:
                self.PUB_KEY = None
                return

            self.PUB_KEY =  request['PUB_KEY']
            self.USERNAME = request['USERNAME'] # TODO test: USERNAME
        else:
            self.PUB_KEY = devPubKey
            self.USERNAME = username
        
        self.addToKeyChain()

    def getID(self):
        return self.ID
    def getAddr(self):
        return self.ADDR
    def getPubKey(self):
        return self.PUB_KEY
    def getUsername(self):
        return self.USERNAME

    def addToKeyChain(self):
        
        authKeyFile = open(Const.AUTH_KEYS_FILE, "r")

        keys = authKeyFile.readlines()
        authKeyFile.close()
        
        pub = str(self.PUB_KEY) + "\n" # anahtarlar içinde ararken "\n" eklenmesi gerekiyor
        
        if not pub in keys:
            authKeyFile = open(Const.AUTH_KEYS_FILE, "a")
            authKeyFile.write(pub)
            return
        
        print(f"[DEVICE] KEY already added to {Const.AUTH_KEYS_FILE}")

    def discoverAddr(self):
        # ID ile IP adresi keşfi
        
        sd = ServiceDiscover(self.ID)
        addr = sd.discover()

        if not addr:
            print(f"[DEVICE] {self.ID} is offline")
        self.ADDR = addr
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
