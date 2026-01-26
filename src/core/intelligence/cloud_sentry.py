import logging
import threading
import time
import hashlib
import requests

class CloudSentry:
    def __init__(self, api_keys=None):
        self.api_keys = api_keys or {}
        self.vt_key = self.api_keys.get("virustotal", "")
        self.abuse_key = self.api_keys.get("abuseipdb", "")
        self.cache = {} # Simple in-memory cache to avoid quota limits

    def check_file_hash(self, file_path, callback=None):
        """
        Async check of file hash against VirusTotal.
        callback: function(result_dict)
        """
        if not self.vt_key:
            return

        # Calculate hash first
        try:
            sha256 = self._get_file_hash(file_path)
        except Exception:
            return

        if sha256 in self.cache:
            if callback:
                callback(self.cache[sha256])
            return

        # Thread the API call
        t = threading.Thread(target=self._query_vt, args=(sha256, callback))
        t.start()

    def check_ip(self, ip_address, callback=None):
        """
        Async check of IP address against AbuseIPDB.
        """
        if not self.abuse_key or ip_address in ["127.0.0.1", "0.0.0.0", "::1"]:
            return

        if ip_address in self.cache:
            if callback:
                callback(self.cache[ip_address])
            return

        t = threading.Thread(target=self._query_abuse_ipdb, args=(ip_address, callback))
        t.start()

    def _query_abuse_ipdb(self, ip, callback):
        url = 'https://api.abuseipdb.com/api/v2/check'
        params = {
            'ipAddress': ip,
            'maxAgeInDays': '90'
        }
        headers = {
            'Accept': 'application/json',
            'Key': self.abuse_key
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                abuse_score = data.get("data", {}).get("abuseConfidenceScore", 0)
                
                result = {
                    "source": "AbuseIPDB",
                    "abuse_score": abuse_score,
                    "target": ip,
                    "country": data.get("data", {}).get("countryCode", "??")
                }
                self.cache[ip] = result
                if callback:
                    callback(result)
            else:
                logging.debug("AbuseIPDB API Error")
        except Exception as e:
            logging.error(f"AbuseIPDB Sentry Error: {e}")

    def _get_file_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _query_vt(self, file_hash, callback):
        url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
        headers = {
            "x-apikey": self.vt_key
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                malicious = stats.get("malicious", 0)
                
                result = {
                    "source": "VirusTotal",
                    "malicious_count": malicious,
                    "suspicious_count": stats.get("suspicious", 0),
                    "hash": file_hash
                }
                self.cache[file_hash] = result
                if callback:
                    callback(result)
            elif response.status_code == 404:
                 self.cache[file_hash] = {"source": "VirusTotal", "status": "unknown"}
            else:
                logging.debug("VirusTotal API Error or Quota Exceeded")
        except Exception as e:
            logging.error(f"Cloud Sentry VT Error: {e}")
