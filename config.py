import os
import sys
import json

from device import Device

CONFIG_DIR = "./.desit/"
CFG_EXT = "json"

DEBUG = "--debug" in sys.argv

class Config:
    
    def __init__(self,
                hostName,       # Host.HOSTNAME
                hostPubKey):    # Host.PUB_KEY
        
        self.HOSTNAME = hostName
        self.PUB_KEY = hostPubKey

        self._config = self.getConfigFromFile() # dict

        self.ID = self.getID()
    
    def getConfigFromFile(self):
        
        try:
            configFile = open(f"{CONFIG_DIR}{self.HOSTNAME}.{CFG_EXT}", "r")
        except FileNotFoundError:
            if DEBUG:
                print(f"[CONFIG] config file doesn't exist")
            
            if not os.path.isdir(CONFIG_DIR):
                os.makedirs(CONFIG_DIR, exist_ok=True)
            
            self.buildConfig()
            configFile = open(f"{CONFIG_DIR}{self.HOSTNAME}.{CFG_EXT}", "r")
        
        cfgDict = json.load(configFile)
        configFile.close()
        
        return cfgDict

    def buildConfig(self):
        
        if DEBUG:
            print(f"[CONFIG] building config file")

        configFile = open(f"{CONFIG_DIR}{self.HOSTNAME}.{CFG_EXT}", "w")
        
        cfgDict = {
            "ID" : None,
            "knownDevices" : []
        }
        
        json.dump(cfgDict, configFile)
        configFile.close()

    def getID(self): # getting host's ID from config file
        return self._config['ID']
    
    def setID(self, newID):
        
        if DEBUG:
            print(f"[CONFIG] changing ID {self._config['ID']} -> {newID}")

        self._config['ID'] = newID

        configFile = open(f"{CONFIG_DIR}{self.HOSTNAME}.{CFG_EXT}", "w")
        
        json.dump(self._config, configFile)
        configFile.close()
    
    def addNewDevice(self, newDevice):
        newID = newDevice.getID()
        knownIDs = [i for i in self._config['knownDevices'] if i['ID'] == newID]
        
        if knownIDs != []:
            print(f"[DEVICE] {newID} is already in config file.")
            return
        
        self._config['knownDevices'].append(
            {
                'ID' : newID,
                'PUB_KEY' : newDevice.getPubKey()
            }
        )

        configFile = open(f"{CONFIG_DIR}{self.HOSTNAME}.{CFG_EXT}", "w")

        json.dump(self._config, configFile)
        configFile.close()

        print(f"[CONFIG] {newID} succesfully added to known devices")
    
    def getKnownDevices(self):

        if self._config['knownDevices'] == []:
            return []
        
        devices = []
        
        for dev in self._config['knownDevices']:
            
            device = Device(dev['ID'],
                            self.HOSTNAME,
                            self.ID,        # Host.ID
                            self.PUB_KEY,
                            dev['PUB_KEY'])
            
            devices.append(device)
        
        return devices