import socket
import queue
import sys
import threading
import zmq
import time
from device import Device
import subprocess
import os
import json
from Messaging import Messaging, MsgType

if "--debug" in sys.argv:
    DEBUG = True
else:
    DEBUG = False

CONFIG_DIR = "./.config/"
KEYS_DIR = "./.config/keys/"
HOST_KEY_DIR = "./.config/hostkey/"

class Host:

    def __init__(self):

        self.HOSTNAME = socket.gethostname()
        self.LOCALHOST = socket.gethostbyname(self.HOSTNAME)
        self.PORT = 6161
        self.HOST_ADDR = (self.LOCALHOST, self.PORT)
        self.FORMAT = "UTF-8"
        self.knownDevices = [] # class Device list
        self.jobQueue = queue.Queue()

        self.PUB_KEY = self.getPubKey() # "alg KEY user@host"
        self.ID = self.PUB_KEY[-16:]    # ID PUB_KEY son 16 karakteri
        
        # TODO build or edit config file

    def start(self):
        
        print(f"WELCOME!")
        print(f"HOST_ADDR: {self.HOST_ADDR}")
        # print(f"LOCAL IP ADDRESS: {self.HOST_ADDR[0]}")
        # print(f"CURRENT GLOBAL PORT: {self.HOST_ADDR[1]}")
        print("[LISTENING] broadcast listening")

        listenBroadcast_T = threading.Thread(target=self.listenBroadcast)
        listenBroadcast_T.start()

        rep_T = threading.Thread(target=self.rep)
        rep_T.start()

        print("Do you want to broadcast?")
        choice = input("[Y/n]: ")
        
        if (choice == "y" or choice == "Y"):
            # msg = f"REQ::CONNECTION ADDR::{self.LOCALHOST} PUB_KEY::{self.PUB_KEY}" # DONE daha yapısal bir msg bulunmalı, json?
            
            brdIP = "192.168.1.255"
            broadcast_T = threading.Thread(target=self.broadcast,
                                        args=(brdIP))
    
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
                print(f"\t[DATA] {data[:24]} ...")

            if address[0] == self.LOCALHOST:
                # kendi broadcast msg görmezden geliniyor.
                continue            

            # RESPONSE = "OK::CONNECTION" # DONE şimdilik
            
            response = Messaging.toDict( MsgType.connectionOK,
                                        self.LOCALHOST,
                                        self.ID)
            reponse = json.dumps(response)
            
            dataDict = json.loads(data)
            
            # if data.startswith("REQ::CONNECTION"):
            if dataDict["TYPE"] == "CONNECTION::REQ":
                # DONE yapısal bir msg yöntemi geçildiğinde PUB_KEY ve IP de msg içinden ayrıştırılmalı
                # duruma göre handleNewClient() gibi bir fn çağırılabilir
                
                print(f"[CONNECTION] {str(server)} requested to connect")
                print(f"\tADDR: {dataDict["ADDR"]}")
                print(f"\tID: {dataDict["ID"]}")
                
                s.sendto(response.encode(self.FORMAT), address)
                print(f"[SENT] {response[:16] + " ... " + response[-20:]} to {str(address)}")

                addNewDevice_T = threading.Thread(target=self.addNewDevice,
                                                    args=(address))
                addNewDevice_T.start()
            
            print("Do you want to add another device [y/n]: ") # FIXME şimdilik
            
            if(input() == "n"):
                break

    def broadcast(self, brdIP):
        # broadcast adresine ilgili mesajı gönderecek fn
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(5)
        
        brdAddr = (brdIP, self.PORT)
        
        # msg = "REQ::CONNECTION" # DONE şimdilik
        
        msg = Messaging.toDict( MsgType.connectionREQ,
                                    self.LOCALHOST,
                                    self.ID)
        msg = json.dumps(msg)
        
        try:
            while True:
                # KILL bu tür mesajlaşma işlemleri \
                #       zeromq kütüphanesi ile yapılmalı.

                print("[SENDING]")
                sent = s.sendto(msg.encode(self.FORMAT), brdAddr)
                
                print("[WAITING]")
                data, server = s.recvfrom(4096)
                data = data.decode(self.FORMAT) 
                
                dataDict = json.loads(data)
                
                # if data.decode(self.FORMAT).startswith("OK::CONNECTION"):
                if dataDict["TYPE"] == "CONNECTION::OK":
                    
                    print(f"[CONNECTION] {str(server)} accepted to connect")
                    print(f"\tADDR: {dataDict["ADDR"]}")
                    print(f"\tID: {dataDict["ID"]}")

                    addNewDevice_T = threading.Thread(target=self.addNewDevice,
                                                        args=(server))
                    addNewDevice_T.start()
                    break
                else:
                    print(f"[FAILED] {str(server)} didn't confirm connection")
                
                print("[LOG] Trying again")

        except TimeoutError as ex:
            print("[BROADCAST] broadcast response timeout")
            print(f"\t{ex}")
            
        finally:
            s.close()
        
    def getPubKey(self): # TODO test: getPubKey()
        
        # mkdir -p ./.config/ 
        # &&
        # ssh-keygen -t ecdsa -b 521 -f ./.config/host-key-ecdsa-521 -N ""  -C "HOSTNAME@LOCALHOST"
        
        if os.path.isdir(HOST_KEY_DIR):
            try:
                keyFile = open(f"{HOST_KEY_DIR}{self.HOSTNAME}.pub", "r")
            except FileNotFoundError:
                if not (os.path.isdir(HOST_KEY_DIR)): # dizin oluşturulmamışsa
                    subprocess.run(["mkdir", "-p", HOST_KEY_DIR])
                
                subprocess.run(["ssh-keygen",
                        "-t", "ecdsa", "-b", "521"            # 521-bit ecdsa
                        "-f", f"{CONFIG_DIR}{self.HOSTNAME}", # key location
                        "-N", "",                             # empty passphrase
                        "-C", f"\"{HOSTNAME}@{LOCALHOST}\""]) # host@localhost

                keyFile = open(f"{HOST_KEY_DIR}{self.HOSTNAME}.pub", "r")
        
        return keyFile.readlines()[0]
        
        # DONE getPUB_KEY(): public-private key oluşturma vs.
        # if (kayıtlı anahtar dosyası)
            # return dosya.PUB_KEY
        # else: 
            #  dosya oluştur & return PUB_KEY

        return "ABC123"
    
    def addNewDevice(self, addr):
        
        # TODO aygıt knownDevices içinde mi? kontrol edilmeli
        
        newDevice = Device(addr)
        self.knownDevices.append(newDevice)

    def rep(self): # TODO test: rep()
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:6162") # DONE REP-REQ portu belirle

        while True:
            #  Wait for next request from client
            message = socket.recv()
            print(f"Received request: {message}")

            #  Do some 'work'
            time.sleep(1)

            if message.startswith("REQ::PUB_KEY"):
                #  Send reply back to client
                socket.send_string(self.getPubKey())

    def getID(self):
        return self.ID