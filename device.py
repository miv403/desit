import zmq
from req_enum import Reqs
from services import ServiceDiscover

class Device:

    def __init__(self, _id):
        self.ID = _id
        self.ADDR = self.getAddr()
        # self.PUB_KEY = self.req(Reqs.PubKey) # TODO test: req()

    def getAddr(self):
        sd = ServiceDiscover(self.ID)
        addr = sd.discover()
        if not addr:
            print(f"[DEVICE] {self.ID} is offline")
        return addr



    def req(self, reqType):
        context = zmq.Context()

        #  Socket to talk to server
        print(f"[REQ] Requesting from {self.ADDR[0]}")
        socket = context.socket(zmq.REQ)
        socket.connect(f"tcp://{self.ADDR[0]}:6162") # TODO REP-REQ portu belirle

        if reqType == Reqs.PubKey:
            print(f"[REQ] Sending request for Reqs.{reqType}")
            socket.send_string("REQ::PUB_KEY")

        #  Get the reply.
        message = socket.recv()
        print(f"[REQ] Received reply from {self.ADDR[0]}: {message}")
        
        return message
