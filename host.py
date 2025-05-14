import json
import os
import socket
import subprocess
import sys
import queue
import threading
import time
import zmq

from config import Config
from device import Device
from messaging import Messaging, MsgType
from services import ServiceRegister

DEBUG = "--debug" in sys.argv

CONFIG_DIR = "./.desit/"
KEYS_DIR = "./.desit/keys/"
HOST_KEY_DIR = "./.desit/hostkey/"

class Host:

    def __init__(self):

        self.HOSTNAME = socket.gethostname()
        self.LOCALHOST = self.getLocalIP()


        self.PUB_KEY = self.getPubKey() # "alg KEY user@host" FIXME test: getPubKey

        self.config = Config(self.HOSTNAME, self.PUB_KEY) # config arayüzü

        self.ID = self.getIDFromConfig()

        # DONE build or edit config file

        self.knownDevices = self.config.getKnownDevices() # class Device list

        self.messaging = Messaging( hostName = self.LOCALHOST,
                                    hostID = self.ID,
                                    pubKey = self.PUB_KEY) # DONE Host.messaging

        self.jobQueue = queue.Queue()

    def start(self):

        print(f"WELCOME!")
        print(f"HOST: {self.HOSTNAME}@{self.LOCALHOST}")
        print(f"HOST ID: {self.ID}")
        
        print("[START] Known devices:")
        for dev in self.knownDevices:
            print(f"\t{dev.getID()} @ {dev.getAddr()}")

        self.service = ServiceRegister(self.ID, 6161, self.LOCALHOST)
        service_T = threading.Thread(target=self.service.register)
        service_T.start()
        
        rep_T = threading.Thread(target=self.rep)
        rep_T.daemon = True
        rep_T.start()


    def getLocalIP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            # gerçekten ulaşılabilir bir adres olması gerekmiyor
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def getPubKey(self): # DONE test: getPubKey()
        
        # mkdir -p ./.config/ 
        # &&
        # ssh-keygen -t ecdsa -b 521 -f ./.config/host-key-ecdsa-521 -N ""  -C "HOSTNAME@LOCALHOST"
        
        try:
            keyFile = open(f"{HOST_KEY_DIR}{self.HOSTNAME}.pub", "r")
        except FileNotFoundError:

            if not os.path.isdir(HOST_KEY_DIR): # dizin oluşturulmamışsa
                os.makedirs(HOST_KEY_DIR, exist_ok=True)

            subprocess.run(["ssh-keygen",
                    "-t", "ecdsa", "-b", "521",           # 521-bit ecdsa
                    "-f", f"{HOST_KEY_DIR}{self.HOSTNAME}", # key location
                    "-N", "",                             # empty passphrase
                    "-C", f"{self.HOSTNAME}@{self.LOCALHOST}"]) # host@localhost

            keyFile = open(f"{HOST_KEY_DIR}{self.HOSTNAME}.pub", "r")
        
        pubKey = keyFile.readline().rstrip('\n')
        keyFile.close()
        
        return pubKey

    def getIDFromConfig(self): # DONE getID fonk.
        
        if not self.config.getID(): # config'de ID None ise yeni
            id_ = self.PUB_KEY.split(" ")[1][-16:].upper() # ID PUB_KEY son 16 karakteri FIXME test: self.ID
            self.config.setID(id_)
            
        return self.config.getID()

    def addNewDevice(self,
                    newID,
                    devPubKey = None):
        
        # DONE aygıt knownDevices içinde mi? kontrol edilmeli
        
        if newID == self.ID:
            print(f"[DEVICE] you can't add your own device")
            return
        
        knownIDs = [i for i in self.knownDevices if i.getID() == newID]
        
        if knownIDs != []:
            print(f"[DEVICE] {newID} is already added.")
            return
        
        newDevice = Device( newID,
                            self.HOSTNAME,
                            self.ID,
                            self.PUB_KEY,
                            devPubKey)

        self.knownDevices.append(newDevice)
        self.config.addNewDevice(newDevice)
        
        print(f"[DEVICE] {newID} succesfully added to known devices")

    def rep(self): # DONE test: rep()
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(f"tcp://{self.LOCALHOST}:6162") # DONE REP-REQ portu belirle
            
        while True:
            #  Wait for next request from client
            message = socket.recv()

            #  Do some 'work'
            time.sleep(1)

            msgDict = json.loads(message)
            print(f"[REP] Received request: {msgDict['TYPE']} from {msgDict['FROM']}")
            
            #if message.startswith("REQ::PUB_KEY"):
            if msgDict['TYPE'] == "REQ::PUB_KEY":
                #  Send reply back to client
                
                # reply with REP::PUB_KEY
                replyDict = self.messaging.toDict(MsgType.repPubKey)
                replyDict['TO'] = msgDict['FROM']
                socket.send_json(replyDict)
                
                self.addNewDevice(msgDict['FROM'], msgDict['PUB_KEY'])

