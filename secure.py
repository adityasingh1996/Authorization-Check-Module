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

def show_header():
   print(f"""
{Fore.RED}--------------------------
Authorization Check Module
--------------------------{Style.RESET_ALL}
""")

def circle_spinner():
   while True:
       for c in ['◜','◠','◝','◞','◡','◟']:
           sys.stdout.write(f'\r{Fore.CYAN}Validating Key {c}{Style.RESET_ALL}')
           sys.stdout.flush()
           time.sleep(0.1)

def validate_access():
   show_header()
   cache_file = '.key_cache'
   current_week = datetime.now().isocalendar()[1]
   current_year = datetime.now().year
   
   if os.path.exists(cache_file):
       with open(cache_file, 'r') as f:
           try:
               cache = json.load(f)
               if cache.get('key') and verify_key(cache['key'], current_year, current_week):
                   print(f"{Fore.GREEN}✓ Using Cached Key{Style.RESET_ALL}")
                   return True
           except:
               pass
   
   while True:
       key = input("\nEnter Key: ").strip()
       stop_spinner = threading.Event()
       
       def spinner_with_stop():
           start_time = time.time()
           while not stop_spinner.is_set() and (time.time() - start_time) < 2:
               for c in ['◜','◠','◝','◞','◡','◟']:
                   if stop_spinner.is_set():
                       break
                   sys.stdout.write(f'\r{Fore.CYAN}Validating Key {c}{Style.RESET_ALL}')
                   sys.stdout.flush()
                   time.sleep(0.1)
       
       spinner = threading.Thread(target=spinner_with_stop)
       spinner.daemon = True
       spinner.start()
       time.sleep(2)
       
       if verify_key(key, current_year, current_week):
           stop_spinner.set()
           sys.stdout.write('\r' + ' '*50 + '\r')
           print(f"{Fore.GREEN}✓ Key Validated{Style.RESET_ALL}")
           with open(cache_file, 'w') as f:
               json.dump({'key': key}, f)
           return True
       
       stop_spinner.set()
       sys.stdout.write('\r' + ' '*50 + '\r')
       print(f"{Fore.RED}✗ Invalid Key{Style.RESET_ALL}")

def verify_key(key, year, week):
   try:
       signature = base64.b64decode(key)
       with open('public_key.pem', 'rb') as f:
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