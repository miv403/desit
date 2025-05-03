import os
import subprocess
import sys
import platform
import json

CONFIG_DIR = "./.desit/"
CONFIG_FILE_EXTENSION = "json"

DEBUG = "--debug" in sys.argv

class Config:
    
    _config = None
    
    def __init__(self, hostname, id_):
        self.HOSTNAME = hostname
        self.ID = id_
        self._config = self.getConfigFromFile() # dict
    
    def getConfigFromFile(self):
        try:
            configFile = open(f"{CONFIG_DIR}{self.HOSTNAME}.{CONFIG_FILE_EXTENSION}", "r")
        except FileNotFoundError:

            if DEBUG:
                print(f"[CONFIG] config file doesn't exist")
            
            print(CONFIG_DIR)
            
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
            "ID" : self.ID,
            "knownDevices" : {
            }
        }
        
        configFile.write(json.dumps(cfgDict))
        configFile.close()

    # def getConfig(self):
    #     return self._config
    
    def setID(self, newID):
        
        if DEBUG:
            print(f"[CONFIG] changing ID {self._config['ID']} -> {newID}")

        self._config['ID'] = newID

        configFile = open(f"{CONFIG_DIR}{self.HOSTNAME}.{CONFIG_FILE_EXTENSION}", "w")
        
        json.dump(self._config, configFile)
        configFile.close()
        
        