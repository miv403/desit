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
            
            printMenu()
            choice = input("? ")
            
            if choice == "1":
                newDevID = input("enter ID: ")
                host.addNewDevice(newDevID)
            elif choice == "2":
                print("file path") # geçici
                pass
            elif choice == "3": # exit
                break
    except Exception as ex:
        print(f"\n[STOP] {ex} closing")
        host.service.stop = True
    finally:
        print("\n[STOP] Finally closing")
        host.service.stop = True

def printMenu():
    print("[1] Add new device")
    print("[2] Add file")
    print("[3] Exit")

if __name__ == "__main__":
    main()
