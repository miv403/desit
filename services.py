from zeroconf import ServiceInfo, Zeroconf, ServiceBrowser, ServiceListener
import socket
import time
import sys

DEBUG = "--debug" in sys.argv

class Listener(ServiceListener):

    def __init__(self, id_):
        self.ID = id_
        self.foundServices = []
    
    def update_service(self, zc, type_, name):
        print(f"[SERVICE LISTENER] {name} updated")
    def remove_service(self, zc, type_, name): # program akışında çalışmıyor
        #if self.foundServices and self.foundServices['name'] == name:
        print(f"[SERVICE LISTENER] {name} was requested to be removed [FIX] {__name__}:{sys._getframe(1).f_lineno}")

    def add_service(self, zc, type_, name):
        info = zc.get_service_info(type_, name)
        print(f"[SERVICE LISTENER] Service {name} added")
        
        if info:
            addresses = ["%s" % socket.inet_ntoa(addr) 
                            for addr in info.addresses]
            if DEBUG:
                print(f"[DEBUG] Found service")
                print(f"\tname: {name}")
                print(f"\ttype: {type_}")
                print(f"\taddresses: {addresses}")
                print(f"\tport: {info.port}")
                print(f"\tserver: {info.server}")

            info.server = str(info.server) # pyright server = None diye hata veriyo
            
            if info.server.split('.')[0] == self.ID:
                # istenen ID eşleşirse bulunan servislere ekleniyor

                self.foundServices.append( {
                    'name' : name,
                    'type' : type_,
                    'addresses' : addresses,
                    'port' : info.port,
                    'server' : info.server
                })
                print(f"[SERVICE LISTENER] Found service: {name} @ {addresses}")

class Service:
    
    def __init__(self, _id, port = None, addr = None):
        self.ID = _id
        self.PORT = port
        self.LOCALHOST = addr
        self.APP_NAME = "desit"
        self.serviceType = f"_{self.APP_NAME}._tcp.local."

        self.stop = False

class ServiceRegister(Service):
    
    def register(self): # mDNS servis kaydı
        if self.PORT == None or self.LOCALHOST == None:
            print(f"[ERROR] cannot register service there is no addr or port provided")
            return

        self.serviceName = self.ID

        serviceInfo = ServiceInfo(
            type_ = self.serviceType,
            name = f"{self.serviceName}.{self.serviceType}",
            addresses = [socket.inet_aton(self.LOCALHOST)],
            port = self.PORT,
            server = f"{self.serviceName}.local",
            properties = {}
        )
        
        zc = Zeroconf()
        print(f"[SERVICE] registering {self.serviceName} @ {self.LOCALHOST}:{self.PORT}")
        zc.register_service(serviceInfo)
        
        try:
            while True:
                if self.stop:
                    break
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally: # FIXME threading'de burası çalışmıyor
            zc.unregister_service(serviceInfo)
            zc.close()
            print(f"[SERVICE] {self.serviceName} unregistered")


class ServiceDiscover(Service):

    def discover(self, timeout = 5):
        
        # istenen ID (_id) için servis araması yapar.
        # bulunan servisin güncel IP adresi geri döndürülür.
        
        zc = Zeroconf()
        listener = Listener(self.ID)
        browser = ServiceBrowser(zc, self.serviceType, listener)
        
        print(f"[DISCOVER] searching {self.ID} with {self.serviceType} for {timeout} secs ")

        time.sleep(timeout)
        zc.close()

        if listener.foundServices != []:
            if DEBUG:
                self.servicePrint(listener.foundServices)
                print(f"[DEBUG] return {listener.foundServices[0]['addresses'][0]}")
            return listener.foundServices[0]['addresses'][0] # bulunan ID için IP adresi döndürülür
        else:
            return None

    def servicePrint(self, service):
        print(f"[DEBUG]")
        if  service != []:
            for s in service:
                    print("\nDiscovered service details:")
                    print(f"Name: {s['name']}") # my-s.myapp._tcp.local.
                    print(f"Type: {s['type']}")
                    print(f"IP Addresses: {', '.join(s['addresses'])}")
                    print(f"Port: {s['port']}")
                    print(f"Server: {s['server']}") # my-s.local.
                    
                    print(f"Device ID: {s['server'].split('.')[0]}")
        else:
            print("[DEBUG] No service found")