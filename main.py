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

    print(f"WELCOME!")
    print(f"LOCAL IP ADDRESS: {host.HOST_ADDR[0]}")
    print(f"CURRENT GLOBAL PORT: {host.HOST_ADDR[1]}")
    
    print("[1]: listen")
    print("[2]: send")
    choice = input("? ")
    
    match choice:
        case "1":
            # thread = threading.Thread(target=ip_disc.listen)
            thread = threading.Thread(target=Host.listenBroadcast, args=(host,))
        case "2":
            # thread = threading.Thread(target=ip_disc.send)
            msg = "REQ::CONNECTION" # FIXME şimdilik
            brdIP = "192.168.1.255"
            thread = threading.Thread(target=Host.broadcast, args=(host, msg, brdIP))

    thread.start()

if __name__ == "__main__":
    main()
    