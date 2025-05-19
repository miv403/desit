import os
import sys
import json

from lib.device import Device
from lib.constants import Const

# CONFIG_DIR = Const.CONFIG_DIR
# CFG_EXT = Const.CFG_EXT

DEBUG = Const.DEBUG

class Config:
    
    def __init__(self,
                hostPubKey):    # Host.PUB_KEY
        
        self.PUB_KEY = hostPubKey

        self._config = self.getConfigFromFile() # dict

        self.ID = self.getID()
    
    def getConfigFromFile(self):
        
        try:
            configFile = open(f"{Const.CONFIG_DIR}{Const.HOSTNAME}.{Const.CFG_EXT}", "r")
        except FileNotFoundError:
            if DEBUG:
                print(f"[CONFIG] config file doesn't exist")
            
            if not os.path.isdir(Const.CONFIG_DIR):
                os.makedirs(Const.CONFIG_DIR, exist_ok=True)
            
            self.buildConfig()
            configFile = open(f"{Const.CONFIG_DIR}{Const.HOSTNAME}.{Const.CFG_EXT}", "r")
        
        cfgDict = json.load(configFile)
        configFile.close()
        
        return cfgDict

    def buildConfig(self):
        
        if DEBUG:
            print(f"[CONFIG] building config file")

        configFile = open(f"{Const.CONFIG_DIR}{Const.HOSTNAME}.{Const.CFG_EXT}", "w")
        
        cfgDict = {
            "ID" : None,
            "knownDevices" : []
        }
        
        json.dump(cfgDict, configFile, indent=4)
        configFile.close()

    def getID(self): # getting host's ID from config file
        return self._config['ID']
    
    def setID(self, newID):
        
        if DEBUG:
            print(f"[CONFIG] changing ID {self._config['ID']} -> {newID}")

        self._config['ID'] = newID

        configFile = open(f"{Const.CONFIG_DIR}{Const.HOSTNAME}.{Const.CFG_EXT}", "w")
        
        json.dump(self._config, configFile, indent=4)
        configFile.close()
    
    def addNewDevice(self, newDevice: Device):
        newID = newDevice.getID()
        knownIDs = [i for i in self._config['knownDevices'] if i['ID'] == newID]
        
        if knownIDs != []:
            print(f"[DEVICE] {newID} is already in config file.")
            return
        
        self._config['knownDevices'].append(
            {
                'ID' : newID,
                'USERNAME' : newDevice.getUsername(),
                'PUB_KEY' : newDevice.getPubKey()
            }
        )

        configFile = open(f"{Const.CONFIG_DIR}{Const.HOSTNAME}.{Const.CFG_EXT}", "w")

        json.dump(self._config, configFile, indent=4)
        configFile.close()

        print(f"[CONFIG] {newID} succesfully added to known devices")
    
    def getKnownDevices(self):

        if self._config['knownDevices'] == []:
            return []
        
        devices = []
        
        for dev in self._config['knownDevices']:
            
            device = Device(dev['ID'],
                            # self.HOSTNAME,
                            self.ID,        # Host.ID
                            self.PUB_KEY,
                            dev['PUB_KEY'],
                            dev['USERNAME'])
            
            devices.append(device)
        
        return devices