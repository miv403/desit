from ip_discovery import ip_disc
import sys
import socket
import threading
from host import Host

if "--debug" in sys.argv:
    DEBUG = True
else:
    DEBUG = False

def main():

    if DEBUG:
        print("debugging...\n\n")

    host = Host()
    host.start()

if __name__ == "__main__":
    main()
    