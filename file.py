import os
import json
from typing import List, Dict

class File:
    def __init__(self, db_path="file_db.json"):
        self.db_path = db_path
        self.fileList: List[Dict] = []
        self._load_file_list()

    def _load_file_list(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as f:
                self.fileList = json.load(f)
        else:
            self.fileList = []
            self._save_file_list()

    def _save_file_list(self):
        with open(self.db_path, 'w') as f:
            json.dump(self.fileList, f, indent=4)

    def addFile(self, filename: str, metadata: Dict):
        new_file = {"filename": filename, "metadata": metadata}
        self.fileList.append(new_file)
        self._save_file_list()

    def updateFile(self, filename: str, new_content: Dict):
        for file in self.fileList:
            if file["filename"] == filename:
                file["metadata"].update(new_content)
                self._save_file_list()
                return True
        return False

    def deleteFile(self, filename: str):
        initial_len = len(self.fileList)
        self.fileList = [f for f in self.fileList if f["filename"] != filename]
        if len(self.fileList) != initial_len:
            self._save_file_list()
            return True
        return False

    def editMetadata(self, filename: str, new_metadata: Dict):
        for file in self.fileList:
            if file["filename"] == filename:
                file["metadata"] = new_metadata
                self._save_file_list()
                return True
        return False

    def listFiles(self) -> List[Dict]:
        return self.fileList
