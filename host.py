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
from file import Files

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
        self.fileManager = Files() # file manager arayüzü

    def start(self):

        print(f"WELCOME!")
        print(f"HOST: {self.HOSTNAME}@{self.LOCALHOST}")
        print(f"HOST ID: {self.ID}")
        
        print("[START] Known devices:")
        for dev in self.knownDevices:#cihazın kimliğini ve adresini yazdırır.
            print(f"\t{dev.getID()} @ {dev.getAddr()}")

        self.service = ServiceRegister(self.ID, 6161, self.LOCALHOST)
        service_T = threading.Thread(target=self.service.register)
        service_T.start()
        
        rep_T = threading.Thread(target=self.rep)
        rep_T.daemon = True
        rep_T.start()

    def getLocalIP(self):#Gerçek bağlantı kurmadan IP'yi tespit eder. 
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            # gerçekten ulaşılabilir bir adres olması gerekmiyor
            ip = s.getsockname()[0] # Bağlantının yerel ucundaki IP adresini verir 
        except Exception:# bağlantı kurma sırasında hata olursa geri dönüş olarak localhost (127.0.0.1) verilir.


            ip = '127.0.0.1'
        finally:
            s.close()#Her durumda soket kapatılır — sistem kaynağı boşa harcanmasın diye.
        return ip #Sonuç olarak elde edilen IP adresi döndürülür.

    def getPubKey(self): # DONE test: getPubKey() 
        
        # mkdir -p ./.config/ 
        # &&
        # ssh-keygen -t ecdsa -b 521 -f ./.config/host-key-ecdsa-521 -N ""  -C "HOSTNAME@LOCALHOST"
        
        try:#ECDSA tabanlı SSH açık anahtarını (public key) üretmek ve okumak için kullanılır.
            keyFile = open(f"{HOST_KEY_DIR}{self.HOSTNAME}.pub", "r")#Anahtarın .pub uzantılı açık anahtar dosyasını okumaya çalışır.
        except FileNotFoundError:

            if not os.path.isdir(HOST_KEY_DIR): # dizin oluşturulmamışsa
                os.makedirs(HOST_KEY_DIR, exist_ok=True) 
                # Anahtar dizini (.config/ gibi) yoksa, oluşturulur.

            subprocess.run(["ssh-keygen",
                    "-t", "ecdsa", "-b", "521", # 521-bit ecdsa
                    "-f", f"{HOST_KEY_DIR}{self.HOSTNAME}", # key location
                    "-N", "", # empty passphrase
                    "-C", f"{self.HOSTNAME}@{self.LOCALHOST}"]) # host@localhost

            keyFile = open(f"{HOST_KEY_DIR}{self.HOSTNAME}.pub", "r")
            # Anahtar üretildikten sonra .pub dosyası tekrar açılır.
        
        pubKey = keyFile.readline().rstrip('\n')
        keyFile.close()
        
        return pubKey #

    def getIDFromConfig(self): # DONE getID fonk.
        
        if not self.config.getID(): # config'de ID None ise yeni
            id_ = self.PUB_KEY.split(" ")[1][-16:].upper() # ID PUB_KEY son 16 karakteri FIXME test: self.ID
            self.config.setID(id_)
            
        return self.config.getID()

    def addNewDevice(self,
                    newID,
                    devPubKey = None):
                    
                    # newID: Eklenmek istenen cihazın kimliği (ID’si),
                    # devPubKey: (İsteğe bağlı) o cihazın public key’i (açık anahtarı). Yoksa None.
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
        context = zmq.Context()# istemcilerden gelen istekleri (request) dinler ve uygun cevapları (reply) gönderir.
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

    def addFileViaMenu(self):
        
        available_files = self.fileManager.listAvailableFiles()

        print("Seçilebilir dosyalar:")
        for i, fName in enumerate(available_files):
            print(f"{i}: {fName}")

        file_index = int(input("Dosya numarasını seçin: "))
        filename = available_files[file_index]

        # Örnek cihaz ID'leri
        knownDevicesList = ["DEV_ID-0", "DEV_ID-1", "DEV_ID-2"]
        knownDevicesList = [devID.getID() for devID in self.knownDevices]
        print("Seçilebilir cihazlar:")
        for i, dev in enumerate(knownDevicesList):
            print(f"{i}: {dev}")

        selected_indices = input("Cihaz numaralarını virgülle girin (örn. 0,2): ")
        selected_ids = [knownDevicesList[int(i)] for i in selected_indices.split(",")]

        success = self.fileManager.addFile(filename, selected_ids)
        if success:
            print("[FILE] File added successfully.")
        else:
            print("[FILE] File cannot be added.")

def add_file_via_menu(self):
    available_files = self.fileManager.listAvailableFiles()
    print("Seçilebilir dosyalar:")
    for i, fname in enumerate(available_files):
        print(f"{i}: {fname}")

    file_index = int(input("Dosya numarasını seçin: "))
    filename = available_files[file_index]

'''
    # Gerçek cihaz ID'lerini çek
    known_devices = self.deviceManager.listKnownDevices()  # <-- bunu kendin implement etmelisin
    print("Seçilebilir cihazlar:")
    for i, dev in enumerate(known_devices):
        print(f"{i}: {dev}")

    selected_indices = input("Cihaz numaralarını virgülle girin (örn. 0,2): ")
    selected_ids = [known_devices[int(i)] for i in selected_indices.split(",")]

    success = self.fileManager.addFile(filename, selected_ids)
    if success:
        print("Dosya başarıyla kaydedildi.")
    else:
        print("Dosya kaydı başarısız.")
'''
