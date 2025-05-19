import json
import os

from lib.constants import Const

class File:
    def __init__(self, path, devIDs):
        self.path = path
        self.devIDs = devIDs
    def getPath(self):
        return self.path
    def getDevIDs(self):
        return self.devIDs

class Files:

    def __init__(self):
        self.fileList = self._loadFileDB()
        self.files = []
        for f in self.fileList:
            self.files.append(File(f['PATH'], f['DEVICES']))

    def _loadFileDB(self):
        if os.path.exists(Const.FILE_DB_DIR): # files.json varsa
            with open(Const.FILE_DB_DIR, 'r') as f:
                return json.load(f)

        return []

    def _saveFileDB(self):
        with open(Const.FILE_DB_DIR, 'w') as f:
            json.dump(self.fileList, f, indent=4)

    def getFiles(self):
        return self.files

    def listAvailableFiles(self):
        """
        .desit/shared/ dizinindeki mevcut dosyaları listeler
        """
        if not os.path.exists(Const.SHARED_DIR):
            os.makedirs(Const.SHARED_DIR)
        return [f for f in os.listdir(Const.SHARED_DIR) if os.path.isfile(os.path.join(Const.SHARED_DIR, f))]

    def addFile(self, filename, device_ids):
        """
        Belirtilen dosyayı belirtilen cihazlara ekler
        """
        file_path = os.path.join(Const.SHARED_DIR, filename)
        if not os.path.exists(file_path):
            print(f"[FILE] File couldn't be found: {file_path}")
            return False

        # Dosya zaten kayıtlı mı kontrol et
        for entry in self.fileList:
            if entry["PATH"] == file_path:
                # Varsa, cihaz listesine ekle
                entry["DEVICES"] = list(set(entry["DEVICES"] + device_ids))
                self._saveFileDB()
                
                self.files.append(File(entry['PATH'], entry['DEVICES']))
                return True

        # Yeni kayıt
        new_entry = {
            "PATH": file_path,
            "DEVICES": device_ids
        }
        self.fileList.append(new_entry)
        
        self.files.append(File(new_entry['PATH'], new_entry['DEVICES']))
        
        self._saveFileDB()
        return True

    def getFileList(self):
        """
        Kayıtlı tüm dosyaları ve eşleştirildikleri cihazları döndürür
        """
        return self.fileList
    
    def removeDevice(self, filename, device_id):
        """
        Belirtilen dosyadan belirtilen cihazı kaldırır
        """
        file_path = os.path.join(Const.SHARED_DIR, filename)
        for entry in self.fileList:
            if entry["PATH"] == file_path and device_id in entry["DEVICES"]:
                entry["DEVICES"].remove(device_id)
                # Cihaz listesi boşsa dosya kaydını kaldır
                if not entry["DEVICES"]:
                    self.fileList.remove(entry)
                self._saveFileDB()
                return True
        return False
    
    def removeFile(self, filename: str) -> bool:
        """
        Belirtilen dosyayı tamamen kaldırır
        """
        file_path = os.path.join(Const.SHARED_DIR, filename)
        initial_len = len(self.fileList)
        self.fileList = [entry for entry in self.fileList if entry["PATH"] != file_path]
        if len(self.fileList) != initial_len:
            self._saveFileDB()
            return True
        return False