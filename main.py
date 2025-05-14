import sys
from host import Host

DEBUG = "--debug" in sys.argv

def main():

    if DEBUG:
        print("debugging...\n\n")

    try:
        host = Host()
        host.start()
        while True: # TODO düzgün ve geçici bir menü
            if input("do you want to add new device? [y/n]: ") == "y":
                newDevID = input("enter ID: ")
                host.addNewDevice(newDevID)
            else:
                break
    except KeyboardInterrupt:
        print("\n[STOP] KeyboardInterrupt closing")
        host.service.stop = True
    finally:
        print("\n[STOP] Finally closing")
        host.service.stop = True
        
    host.service.stop = True


if __name__ == "__main__":
    main()
