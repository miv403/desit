import zmq
from req_enum import Reqs

class Device:
    
    def __init__(self, addr):
        
        self.ADDR = addr
        self.ID = self.req(Reqs.getID)
        
    
    def getID(self):    # get() for ID
        return self.ID

    def req(self, reqType):
        context = zmq.Context()

        #  Socket to talk to server
        print(f"[REQ] Requesting from {self.ADDR[0]}")
        socket = context.socket(zmq.REQ)
        socket.connect(f"tcp://{self.ADDR[0]}:5555")

        if reqType == Reqs.getID:
            print(f"[REQ] Sending request for Reqs.{reqType}")
            socket.send_string("REQ::ID")

        #  Get the reply.
        message = socket.recv()
        print(f"[REQ] Received reply from {self.ADDR[0]}: {message}")
        
        return message
