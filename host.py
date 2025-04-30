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
from messaging import Messaging, MsgType
from services import ServiceRegister

DEBUG = "--debug" in sys.argv

CONFIG_DIR = "./.config/"
KEYS_DIR = "./.config/keys/"
HOST_KEY_DIR = "./.config/hostkey/"

class Host:

    def __init__(self):

        self.HOSTNAME = socket.gethostname()
        # self.LOCALHOST = socket.gethostbyname(self.HOSTNAME)
        self.LOCALHOST = self.getLocalIP()
        # self.PORT = 6161 # FIXME  bu sadece mDNS için, 
        # self.HOST_ADDR = (self.LOCALHOST, self.PORT)
        # self.FORMAT = "UTF-8"
        self.knownDevices = [] # class Device list
        self.jobQueue = queue.Queue()
        self.messaging = Messaging()
        
        # self.PUB_KEY = self.getPubKey() # "alg KEY user@host" FIXME test: getPubKey
        #self.ID = self.PUB_KEY[-16:]    # ID PUB_KEY son 16 karakteri FIXME test: self.ID
        self.ID = "9876A" # FIXME geçici ID
        # TODO build or edit config file

    def start(self):

        print(f"WELCOME!")
        print(f"HOST: {self.HOSTNAME}@{self.LOCALHOST}")
        print(f"HOST ID: {self.ID}")
        
        service = ServiceRegister(self.ID, 6161, self.LOCALHOST)
        service_T = threading.Thread(target=service.register)
        service_T.start()
        try:
            while True:
                if input("do you want to add new device? [y/n]: ") == "y":
                    newDevID = input("enter ID: ")
                    newDev = Device(newDevID)
                    if newDev.ADDR != None:
                        pass
                    else:
                        # if newDev not in knownDevices
                        # then .append(newDev)
                        # else
                        # print( already added)
                        pass
                else:
                    break
        except KeyboardInterrupt:
            print("\n KeyboardInterrupt closing")
            exit()

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
            if not (os.path.isdir(HOST_KEY_DIR)): # dizin oluşturulmamışsa
                subprocess.run(["mkdir", "-p", HOST_KEY_DIR]) # FIXME windows için çalışmıyor
            
            subprocess.run(["ssh-keygen",
                    "-t", "ecdsa", "-b", "521"            # 521-bit ecdsa
                    "-f", f"{CONFIG_DIR}{self.HOSTNAME}", # key location
                    "-N", "",                             # empty passphrase
                    "-C", f"\"{self.HOSTNAME}@{self.LOCALHOST}\""]) # host@localhost

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

    def getID(self): # FIXME getID fonk.
        return self.ID

