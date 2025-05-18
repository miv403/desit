import os
import json
from typing import List, Dict

class File:
    def __init__(self, shared_dir=".desit/shared/", db_path="files.json"):
        self.shared_dir = shared_dir
        self.db_path = db_path
        self.files: List[Dict] = self._load_file_db()

    def _load_file_db(self) -> List[Dict]:
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as f:
                return json.load(f)
        return []

    def _save_file_db(self):
        with open(self.db_path, 'w') as f:
            json.dump(self.files, f, indent=4)

    def listAvailableFiles(self) -> List[str]:
        """
        .desit/shared/ dizinindeki mevcut dosyaları listeler
        """
        if not os.path.exists(self.shared_dir):
            os.makedirs(self.shared_dir)
        return [f for f in os.listdir(self.shared_dir) if os.path.isfile(os.path.join(self.shared_dir, f))]

    def addFile(self, filename: str, device_ids: List[str]) -> bool:
        """
        Belirtilen dosyayı belirtilen cihazlara ekler
        """
        file_path = os.path.join(self.shared_dir, filename)
        if not os.path.exists(file_path):
            print(f"[!] Dosya bulunamadı: {file_path}")
            return False

        # Dosya zaten kayıtlı mı kontrol et
        for entry in self.files:
            if entry["PATH"] == file_path:
                # Varsa, cihaz listesine ekle
                entry["DEVICES"] = list(set(entry["DEVICES"] + device_ids))
                self._save_file_db()
                return True

        # Yeni kayıt
        new_entry = {
            "PATH": file_path,
            "DEVICES": device_ids
        }
        self.files.append(new_entry)
        self._save_file_db()
        return True

    def getFileList(self) -> List[Dict]:
        """
        Kayıtlı tüm dosyaları ve eşleştirildikleri cihazları döndürür
        """
        return self.files
    
    def removeDevice(self, filename: str, device_id: str) -> bool:
        """
        Belirtilen dosyadan belirtilen cihazı kaldırır
        """
        file_path = os.path.join(self.shared_dir, filename)
        for entry in self.files:
            if entry["PATH"] == file_path and device_id in entry["DEVICES"]:
                entry["DEVICES"].remove(device_id)
                # Cihaz listesi boşsa dosya kaydını kaldır
                if not entry["DEVICES"]:
                    self.files.remove(entry)
                self._save_file_db()
                return True
        return False
    
    def removeFile(self, filename: str) -> bool:
        """
        Belirtilen dosyayı tamamen kaldırır
        """
        file_path = os.path.join(self.shared_dir, filename)
        initial_len = len(self.files)
        self.files = [entry for entry in self.files if entry["PATH"] != file_path]
        if len(self.files) != initial_len:
            self._save_file_db()
            return True
        return False