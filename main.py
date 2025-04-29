import sys
import socket
import threading
from host import Host

DEBUG = "--debug" in sys.argv

def main():

    if DEBUG:
        print("debugging...\n\n")

    host = Host()
    host.start()

if __name__ == "__main__":
    main()
