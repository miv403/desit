import socket
import sys
import getpass

class Const: # TODO implement global constants

    DEBUG = "--debug" in sys.argv

    CFG_EXT = "json" # config extension
    HOME_DIR = None # TODO get user name and build ~/
    CONFIG_DIR = "./.desit/"
    FILE_DB_DIR = f"{CONFIG_DIR}files.{CFG_EXT}"
    KEYS_DIR = "./.desit/keys/"
    HOST_KEY_DIR = "./.desit/hostkey/"
    SHARED_DIR = "./.desit/shared/"
    HOSTNAME = socket.gethostname()
    # HOST_PUB_KEY = Host.getPubKey(self)
    # LOCALHOST = Host.getLocalIP()
    USERNAME = getpass.getuser()
