import socket
import queue
import sys

if "--debug" in sys.argv:
    DEBUG = True
else:
    DEBUG = False

class Host:

    def __init__(self):
        self.LOCALHOST = socket.gethostbyname(socket.gethostname())
        self.PORT = 6161
        self.HOST_ADDR = (self.LOCALHOST, self.PORT)
        self.FORMAT = "UTF-8"
        self.knownDevices = []
        self.jobQueue = queue.Queue()

    def listenBroadcast(self):
        
        # broadcast mesajlarını dinleyip ilgili mesaja göre
        # başka fonksiyonları çağırır
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(self.HOST_ADDR)
        
        while True:
            data, address = s.recvfrom(4096)
            data = str(data.decode(self.FORMAT))
            
            if DEBUG:
                print(f"[MSG] {len(data)}B from {str(address)}")
                print(f"\t[DATA] {data}")
            
            RESPONSE = "OK::CONNECTION" # FIXME şimdilik
            
            if data.startswith("REQ::CONNECTION"): # FIXME şimdilik
                # duruma göre handleNewClient() gibi bir fn çağırılabilir
                s.sendto(RESPONSE.encode(self.FORMAT), address)
                print(f"[SENT] {RESPONSE} to {str(address)}")
            
            print("Do you want to add another device [y/n]") # FIXME şimdilik
            
            if(input() == "n"):
                break

    def broadcast(self, msg, brdIP):
        # broadcast adresine ilgili mesajı gönderecek fn
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(5)
        
        brdAddr = (brdIP, self.PORT)
        
        msg = "REQ::CONNECTION" # FIXME şimdilik
        
        try:
            while True:
                # TODO bu tür mesajlaşma işlemleri \
                #       zeromq kütüphanesi ile yapılmalı.

                print("[SENDING] ")
                sent = s.sendto(msg.encode(self.FORMAT), brdAddr)
                
                print("[WAITING]")
                data, server = s.recvfrom(4096)
                
                if data.decode(self.FORMAT).startswith("OK::CONNECTION"):
                    print(f"[CONNECTION] {str(server)} accepted to connect")

                    self.knownDevices.append(server)
                    break
                else:
                    print(f"[FAILED] {str(server)} didn't confirm connection")
                
                print("[LOG] Trying again")

        except TimeoutError as ex:
            print("broadcast response timeout")
            print(f"\t{ex}")
            
        finally:
            s.close()