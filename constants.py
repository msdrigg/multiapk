import os

import re


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

LIB_PATH = os.path.join(PROJECT_ROOT, "lib")
ADB_PATH = os.path.join(LIB_PATH, "adb.exe")

IP_MATCHER = re.compile("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?:\:[0-9]{1,5})?$")
