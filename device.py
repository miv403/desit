import zmq

class Device:
    
    def __init__(self, addr):
        
        self.ADDR = addr
        self.ID = self.reqID()
        
    
    def getID(self):
        
        return self.ID

    def reqID(self):
        context = zmq.Context()

        #  Socket to talk to server
        print("Connecting to hello world server...")
        socket = context.socket(zmq.REQ)
        socket.connect(f"tcp://{self.ADDR[0]}:5555")

        print(f"Sending request {request} ...")
        socket.send_string("REQ::ID")

        #  Get the reply.
        message = socket.recv()
        print(f"Received reply {request} [ {message} ]")
        
        return message