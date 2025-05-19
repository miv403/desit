import socket
import sys
import getpass
import os

class Const: # TODO implement global constants

    DEBUG = "--debug" in sys.argv

    HOSTNAME = socket.gethostname()
    USERNAME = getpass.getuser()

    CFG_EXT = "json" # config extension

    # DIRs
    CWD = os.path.dirname(os.path.abspath(__file__)) # TODO implement it
    HOME_DIR = os.environ['HOME']

    AUTH_KEYS_FILE = f"{HOME_DIR}/.ssh/authorized_keys"
    CONFIG_DIR = f"{HOME_DIR}/.desit/"
    SHARED_DIR = f"{HOME_DIR}/.desit/shared/"
    HOST_KEY_DIR = f"{HOME_DIR}/.desit/hostkey/"
    KEYS_DIR = f"{HOME_DIR}/.desit/keys/"
    FILE_DB_DIR = f"{CONFIG_DIR}files.{CFG_EXT}"
    
    # HOST_PUB_KEY = Host.getPubKey(self)
    # LOCALHOST = Host.getLocalIP()
