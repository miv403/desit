import json
import os
import platform
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

KEYS_DIR = "./.desit/keys/"
CONFIG_DIR = "./.desit/"
HOST_KEY_DIR = "./.desit/hostkey/"

class Host:

    def __init__(self):

        self.HOSTNAME = socket.gethostname()
        self.LOCALHOST = self.getLocalIP()

        self.config = Config(self.HOSTNAME) # config arayüzü

        self.PUB_KEY = self.getPubKey() # "alg KEY user@host" FIXME test: getPubKey

        self.ID = self.getIDFromConfig()
        # TODO build or edit config file

        self.knownDevices = self.config.getKnownDevices() # class Device list

        self.jobQueue = queue.Queue()
        self.messaging = Messaging()

    def start(self):

        print(f"WELCOME!")
        print(f"HOST: {self.HOSTNAME}@{self.LOCALHOST}")
        print(f"HOST ID: {self.ID}")
        
        print("[START] Known devices:")
        for dev in self.knownDevices:
            print(f"\t{dev.getID()} @ {dev.getAddr()}")

        service = ServiceRegister(self.ID, 6161, self.LOCALHOST)
        service_T = threading.Thread(target=service.register)
        service_T.start()
        try:
            while True: # TODO düzgün ve geçici bir menü
                if input("do you want to add new device? [y/n]: ") == "y":
                    newDevID = input("enter ID: ")
                    self.addNewDevice(newDevID)
                else:
                    break
        except KeyboardInterrupt:
            print("\n[STOP] KeyboardInterrupt closing")
            service.stop = True # TODO service.stop daha düzgün bir kapama yöntemi bulunabilir
            exit()
        
        service.stop = True # TODO service.stop daha düzgün bir kapama yöntemi bulunabilir
        
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

    def getPubKey(self): # TODO test: getPubKey()
        
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
                    "-C", f"\"{self.HOSTNAME}@{self.LOCALHOST}\""]) # host@localhost

            keyFile = open(f"{HOST_KEY_DIR}{self.HOSTNAME}.pub", "r")
        
        return keyFile.readline()

    def getIDFromConfig(self): # DONE getID fonk.
        
        if not self.config.getID():
            id_ = self.PUB_KEY.split(" ")[1][-16:].upper() # ID PUB_KEY son 16 karakteri FIXME test: self.ID
            self.config.setID(id_)
            
        return self.config.getID()

    def addNewDevice(self, newID):
        
        # TODO aygıt knownDevices içinde mi? kontrol edilmeli
        
        if newID == self.ID:
            print(f"[DEVICE] you can't add your own device")
            return
        
        knownIDs = [i for i in self.knownDevices if i.getID() == newID]
        
        if knownIDs != []:
            print(f"[DEVICE] {newID} is already added.")
            return
        
        newDevice = Device(newID)

        self.knownDevices.append(newDevice)
        self.config.addNewDevice(newID)

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
