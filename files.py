import os
import json
from constants import Const

class Files:
    def __init__(self):
        self.files = self._loadFileDB()

    def _loadFileDB(self):
        if os.path.exists(Const.FILE_DB_DIR): # files.json varsa
            with open(Const.FILE_DB_DIR, 'r') as f:
                return json.load(f)

        return []

    def _saveFileDB(self):
        with open(Const.FILE_DB_DIR, 'w') as f:
            json.dump(self.files, f, indent=4)

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
        for entry in self.files:
            if entry["PATH"] == file_path:
                # Varsa, cihaz listesine ekle
                entry["DEVICES"] = list(set(entry["DEVICES"] + device_ids))
                self._saveFileDB()
                return True

        # Yeni kayıt
        new_entry = {
            "PATH": file_path,
            "DEVICES": device_ids
        }
        self.files.append(new_entry)
        self._saveFileDB()
        return True

    def getFileList(self):
        """
        Kayıtlı tüm dosyaları ve eşleştirildikleri cihazları döndürür
        """
        return self.files
    
    def removeDevice(self, filename, device_id):
        """
        Belirtilen dosyadan belirtilen cihazı kaldırır
        """
        file_path = os.path.join(Const.SHARED_DIR, filename)
        for entry in self.files:
            if entry["PATH"] == file_path and device_id in entry["DEVICES"]:
                entry["DEVICES"].remove(device_id)
                # Cihaz listesi boşsa dosya kaydını kaldır
                if not entry["DEVICES"]:
                    self.files.remove(entry)
                self._saveFileDB()
                return True
        return False
    
    def removeFile(self, filename: str) -> bool:
        """
        Belirtilen dosyayı tamamen kaldırır
        """
        file_path = os.path.join(Const.SHARED_DIR, filename)
        initial_len = len(self.files)
        self.files = [entry for entry in self.files if entry["PATH"] != file_path]
        if len(self.files) != initial_len:
            self._saveFileDB()
            return True
        return False