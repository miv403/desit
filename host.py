import socket
import queue
import sys
import threading
from device import Device

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
        self.knownDevices = [] # class Device list
        self.jobQueue = queue.Queue()

        self.ID = self.getID()

        print(f"WELCOME!")
        print(f"HOST_ADDR: {self.HOST_ADDR}")
        # print(f"LOCAL IP ADDRESS: {self.HOST_ADDR[0]}")
        # print(f"CURRENT GLOBAL PORT: {self.HOST_ADDR[1]}")

        print("[LISTENING] broadcast listening")

        listenBroadcast_T = threading.Thread(target=self.listenBroadcast)
        listenBroadcast_T.start()

        # print("[1]: listen")
        # print("[2]: send")
        # choice = input("? ")

        print("Do you want to broadcast?")
        choice = input("[Y/n]: ")
        
        if (choice == "y" or choice == "Y"):
            
            msg = f"REQ::CONNECTION ADDR::{self.LOCALHOST} ID::{self.ID}" # FIXME daha yapısal bir msg bulunmalı, json?
            brdIP = "192.168.1.255"
            broadcast_T = threading.Thread(target=self.broadcast,
                                        args=(msg, brdIP))
    
            broadcast_T.start()

    def listenBroadcast(self):
        
        # broadcast mesajlarını dinleyip ilgili mesaja göre
        # başka fonksiyonları çağırır
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(self.HOST_ADDR)
        
        while True:
            data, address = s.recvfrom(4096)
            data = str(data.decode(self.FORMAT))
            
            if DEBUG:
                print("[DEBUG]")
                print(f"\t[MSG] {len(data)}B from {str(address)}")
                print(f"\t[DATA] {data}")
            
            RESPONSE = "OK::CONNECTION" # FIXME şimdilik
            
            if address[0] == self.HOST_ADDR[0]:
                # kendi broadcast msg görmezden geliniyor.
                continue
            
            if data.startswith("REQ::CONNECTION"):
                # FIXME yapısal bir msg yöntemi geçildiğinde ID ve IP de msg içinden ayrıştırılmalı
                # duruma göre handleNewClient() gibi bir fn çağırılabilir
                
                devID = "9876" # FIXME gelen string içerisinden temin edilmeli
                
                
                s.sendto(RESPONSE.encode(self.FORMAT), address)
                print(f"[SENT] {RESPONSE} to {str(address)}")

                addNewDevice_T = threading.Thread(target=self.addNewDevice,
                                                    args=(address))
                addNewDevice_T.start()
            
            print("Do you want to add another device [y/n]: ") # FIXME şimdilik
            
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

                print("[SENDING]")
                sent = s.sendto(msg.encode(self.FORMAT), brdAddr)
                
                print("[WAITING]")
                data, server = s.recvfrom(4096)
                
                devID = "9876"
                
                if data.decode(self.FORMAT).startswith("OK::CONNECTION"):
                    print(f"[CONNECTION] {str(server)} accepted to connect")

                    addNewDevice_T = threading.Thread(target=self.addNewDevice,
                                                        args=(server))
                    addNewDevice_T.start()

                    break
                else:
                    print(f"[FAILED] {str(server)} didn't confirm connection")
                
                print("[LOG] Trying again")

        except TimeoutError as ex:
            print("broadcast response timeout")
            print(f"\t{ex}")
            
        finally:
            s.close()
        
    def getID(self):
        
        # TODO getID(): public-private key oluşturma vs.
        # if (kayıtlı anahtar dosyası)
            # return dosya.ID
        # else: 
            #  dosya oluştur & return ID
        
        return "ABC123"
    
    def addNewDevice(self, addr):
        
        newDevice = Device(addr,devID)
        self.knownDevices.append(newDevice)
        
        
    def replyID():
        
        pass