from datetime import datetime
import base64
import json
import os
import sys
import time
import threading
from colorama import init, Fore, Style
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

init()

# Constants and paths
SECURE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_KEY_PATH = os.path.join(SECURE_DIR, 'public_key.pem')
CACHE_FILE = os.path.join(SECURE_DIR, '.key_cache')
VALIDATION_DURATION = 2

def show_header():
   print(f"""
{Fore.RED}--------------------------
Authorization Check Module
--------------------------{Style.RESET_ALL}
""")

class SpinnerThread(threading.Thread):
   def __init__(self):
       super().__init__(daemon=True)
       self.stop_event = threading.Event()
       
   def run(self):
       start_time = time.time()
       while not self.stop_event.is_set() and (time.time() - start_time) < VALIDATION_DURATION:
           for c in ['◜','◠','◝','◞','◡','◟']:
               if self.stop_event.is_set():
                   break
               sys.stdout.write(f'\r{Fore.CYAN}Validating Key {c}{Style.RESET_ALL}')
               sys.stdout.flush()
               time.sleep(0.1)
               
   def stop(self):
       self.stop_event.set()

def check_root():
   if os.geteuid() != 0:
       print(f"{Fore.RED}Error: This script requires root privileges{Style.RESET_ALL}")
       sys.exit(1)
       
def validate_access():
   show_header()
   check_root()
   current_week = datetime.now().isocalendar()[1]
   current_year = datetime.now().year
   
   if os.path.exists(CACHE_FILE):
       with open(CACHE_FILE, 'r') as f:
           try:
               cache = json.load(f)
               if cache.get('key') and verify_key(cache['key'], current_year, current_week):
                   print(f"{Fore.GREEN}✓ Using Cached Key{Style.RESET_ALL}")
                   return True
           except:
               pass
   
   while True:
       key = input("\nEnter Key: ").strip()
       spinner = SpinnerThread()
       spinner.start()
       time.sleep(VALIDATION_DURATION)
       
       if verify_key(key, current_year, current_week):
           spinner.stop()
           sys.stdout.write('\r' + ' '*50 + '\r')
           print(f"{Fore.GREEN}✓ Key Validated{Style.RESET_ALL}")
           with open(CACHE_FILE, 'w') as f:
               json.dump({'key': key}, f)
           return True
       
       spinner.stop()
       sys.stdout.write('\r' + ' '*50 + '\r')
       print(f"{Fore.RED}✗ Invalid Key{Style.RESET_ALL}")

def verify_key(key, year, week):
   try:
       signature = base64.b64decode(key)
       with open(PUBLIC_KEY_PATH, 'rb') as f:
           public_key = serialization.load_pem_public_key(f.read())
       public_key.verify(
           signature,
           f"{year}:{week}".encode(),
           padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
           salt_length=padding.PSS.MAX_LENGTH),
           hashes.SHA256()
       )
       return True
   except:
       return False
