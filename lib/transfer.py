import subprocess

from lib.constants import Const

# HOST_KEY_DIR_TEMP = f"{Const.HOME_DIR}/proje/src/.desit/hostkey/"

class Transfer:
    
    def send(self, file, devices):
        
        filePath = file.getPath()
        
        for device in devices:
            username = device.getUsername() 
            addr = device.discoverAddr()
            
            print(f"[TRANSFER] Sending {filePath}")
            # rsync --mkpath -e "ssh -i /home/miv/proje/src/.desit/hostkey/deb12-miv" ./.desit/shared/file-007.dat mivlab@192.168.1.24:/home/mivlab/.desit/shared/
            command =  [
                "rsync",
                "--mkpath",
                "-e",
                f'ssh -i {Const.HOST_KEY_DIR}{Const.HOSTNAME}',
                f"{filePath}",
                f"{username}@{addr}:/home/{username}/.desit/shared/"
                ]
                
            if Const.DEBUG:
                print("[TRANSFER] executing: ", end="")
                print(' '.join(command))
                
            subprocess.run(command)
