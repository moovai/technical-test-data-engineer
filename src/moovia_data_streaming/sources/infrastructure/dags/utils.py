import sys
import os

def set_full_package_path(path: str):
  is_windows = hasattr(sys, 'getwindowsversion')
 
  ROOT_DIR = os.path.abspath(os.curdir)
  ROOT_DIR = ROOT_DIR.split('src')[0]  
  if is_windows:
     path = path.replace('/', '\\')   
  package_path = f'{ROOT_DIR}{path}'    
  sys.path.insert(0, package_path)   