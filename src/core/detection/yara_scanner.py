import yara
import os
import logging

class YaraScanner:
    def __init__(self, rules_dir):
        self.rules_dir = rules_dir
        self.rules = None
        self.compiled = False
        self._compile_rules()

    def _compile_rules(self):
        filepaths = {}
        if not os.path.exists(self.rules_dir):
            logging.warning(f"YARA rules directory {self.rules_dir} not found.")
            return

        for f in os.listdir(self.rules_dir):
            if f.endswith(".yar") or f.endswith(".yara"):
                filepaths[f] = os.path.join(self.rules_dir, f)
        
        if not filepaths:
            logging.warning("No YARA rules found.")
            return

        try:
            self.rules = yara.compile(filepaths=filepaths)
            self.compiled = True
            logging.info(f"Compiled {len(filepaths)} YARA rule files.")
        except yara.Error as e:
            logging.error(f"YARA compilation error: {e}")

    def scan_file(self, file_path):
        if not self.compiled or not os.path.exists(file_path):
            return []
        
        try:
            matches = self.rules.match(file_path)
            return [str(m) for m in matches]
        except Exception as e:
             # logging.error(f"YARA scan error for {file_path}: {e}")
             return []
