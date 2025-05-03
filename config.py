import os
import subprocess
import sys
import platform
import json

from device import Device

CONFIG_DIR = "./.desit/"
CONFIG_FILE_EXTENSION = "json"

DEBUG = "--debug" in sys.argv

class Config:
    
    _config = None
    
    def __init__(self, hostname):
        self.HOSTNAME = hostname
        self._config = self.getConfigFromFile() # dict
    
    def getConfigFromFile(self):
        try:
            configFile = open(f"{CONFIG_DIR}{self.HOSTNAME}.{CONFIG_FILE_EXTENSION}", "r")
        except FileNotFoundError:
            if DEBUG:
                print(f"[CONFIG] config file doesn't exist")
            
            if not os.path.isdir(CONFIG_DIR):
                os.makedirs(CONFIG_DIR, exist_ok=True)
            
            self.buildConfig()
            configFile = open(f"{CONFIG_DIR}{self.HOSTNAME}.{CONFIG_FILE_EXTENSION}", "r")
        
        confDict = json.load(configFile)
        configFile.close()

        return confDict

    def buildConfig(self):
        
        if DEBUG:
            print(f"[CONFIG] building config file")

        configFile = open(f"{CONFIG_DIR}{self.HOSTNAME}.{CONFIG_FILE_EXTENSION}", "w")
        
        cfgDict = {
            "ID" : None,
            "knownDevices" : []
        }
        
        configFile.write(json.dumps(cfgDict))
        configFile.close()

    def getID(self): # getting host's ID from config file
        return self._config['ID']
    
    def setID(self, newID):
        
        if DEBUG:
            print(f"[CONFIG] changing ID {self._config['ID']} -> {newID}")

        self._config['ID'] = newID

        configFile = open(f"{CONFIG_DIR}{self.HOSTNAME}.{CONFIG_FILE_EXTENSION}", "w")
        
        json.dump(self._config, configFile)
        configFile.close()
    
    def addNewDevice(self, newID):
        pass
        knownIDs = [i for i in self._config['knownDevices'] if i['ID'] == newID]
        
        if knownIDs != []:
            print(f"[DEVICE] {newID} is already in config file.")
            return
        
        
        
        self._config['knownDevices'].append(
            {
                'ID' : newID
            }
        )

        configFile = open(f"{CONFIG_DIR}{self.HOSTNAME}.{CONFIG_FILE_EXTENSION}", "w")
        json.dump(self._config, configFile)
        configFile.close()
    
    def getKnownDevices(self):

        if self._config['knownDevices'] == []:
            return []
        
        devices = []
        
        for dev in self._config['knownDevices']:
            
            device = Device(dev['ID'])
            
            devices.append(device)
        
        return devices