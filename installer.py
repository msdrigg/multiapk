import os

import subprocess as sp
import re
from typing import List, Tuple
import warnings
from enum import Enum

from constants import ADB_PATH, IP_MATCHER


class ConnectionState(Enum):
    CONNECTED = "device"
    DISCONNECTED = "offline"
    UNAUTHORIZED = "unauthorized"


class ADBError(RuntimeError):
    def __init__(self, code: int = 1, message: str = None):
        self.code = code
        self.message = message


class Device:
    def __init__(self, ip_address, connection_state=ConnectionState.DISCONNECTED):
        super()
        if IP_MATCHER.match(ip_address):
            warnings.warn(
                f"Cannot create device with invalid ip adderss: {ip_address}"
            )
        self.ip_address = ip_address
        self.connection_state = connection_state
    

class ADB:
    def __init__(self, path=ADB_PATH):
        super()
        self.path = ADB_PATH
        self.check_adb()
        
    def check_adb(self):
        if not os.path.isfile(self.path):
            raise ValueError(f"ADB_PATH provided {ADB_PATH} is not a valid path to the adb executable")
    
    def _execute_command(self, *args, tries=1, check_err=True, check_adb_on_error=False) -> sp.CompletedProcess:
        cmd = None
        for i in range(tries):
            try:
                cmd = sp.run(
                    self.path,
                    *args,
                    stdout=sp.PIPE,
                    stderr=sp.PIPE,
                    text=True
                )
                cmd.check_returncode()
                return cmd
            except sp.CalledProcessError as err:
                if i == tries - 1 and check_err:
                    if check_adb_on_error:
                        self.check_adb()
                    raise err
        return cmd
    
    def kill_server(self):
        self._execute_command("kill-server", tries=2, check_adb_on_error=True)
    
    def start_server(self):
        self._execute_command("start-server", tries=2, check_adb_on_error=True)

    def devices(self) -> List[Device]:
        cmd = self._execute_command("devices", tries=2, check_adb_on_error=True)
        
        device_list = cmd.stdout.splitlines()
        return list(
            map(
                lambda a: Device(
                    a.split()[0],
                    ConnectionState[a.split()[1]]
                ),
                device_list
            )
        )
    
    def connect(self, device: Device):
        self._execute_command(
            "connect",
            device.ip_address,
            tries=2,
            check_adb_on_error=True
        )

    def disconnect(self, device: Device = None):
        extra_args = []
        if device is not None:
            extra_args.append(device.ip_address)
        
        self._execute_command(
            "disconnect", *extra_args, tries=2
        )
    
    @staticmethod
    def get_device_args(device: Device):
        extra_args = []
        if device is not None:
            extra_args.append("-s")
            extra_args.append(device.ip_address)

    def shell(self, *args, device: Device = None, tries=1):
        extra_args = ADB.get_device_args(device)
        
        self._execute_command(
            *extra_args,
            "shell",
            *args,
            tries=tries
        )
    
    def install(self, package, device: Device = None):
        extra_args = ADB.get_device_args(device)
        
        self._execute_command(
            *extra_args,
            "install",
            package
        )
    
    def uninstall(self, package, device: Device = None):
        extra_args = ADB.get_device_args(device)
        
        no_package_search = re.compile(
            f"^\s*java.lang.IllegalArgumentException:\sUnknown package:\s{package}\s*$",
            flags=re.MULTILINE
        )

        try:
            cmd = self._execute_command(
                *extra_args,
                "uninstall",
                package,
                check_err=False
            )
        except sp.CalledProcessError as err:
            # Handle error from no package
            if (err.stderr is not None and no_package_search.search(err.stderr)) or \
                (err.stdout is not None and no_package_search.search(err.stdout)):
                return False
            else:
                raise err
        
        if (err.stderr is not None and no_package_search.search(err.stderr)) or \
            (err.stdout is not None and no_package_search.search(err.stdout)):
            return False

        return True
    
    def check_connection(self, device) -> ConnectionState:
        for own_device in self.devices():
            if own_device.ip_address.split(":")[0] == device.ip_address.split(":")[0]:
                return own_device.connection_state
        return False


class Installer:
    def __init__(self, device: Device, apk_path, adb: ADB = ADB(ADB_PATH)):
        super()
        self.device = device
        self.adb = adb
        self.device_state = ConnectionState.DISCONNECTED
        self.apk_path = apk_path

    def connect(self): 
        self.adb.connect(self.device)

    def reconnect(self, hard=False):
        if hard:
            self.adb.kill_server()
        else:
            self.adb.disconnect()
        self.connect()
    
    def check_connection(self) -> ConnectionState:
        try:
            return self.adb.check_connection(self.device)
        except sp.CalledProcessError:
            return ConnectionState.DISCONNECTED
    
    def restart_server(self):
        self.adb.kill_server()
        self.adb.start_server()
    
    def ensure_connection(self):
        # Starts an event loop to make sure the device is connected
        while True:
            handle = self.connect()
            
            result = self.check_connection()
            if result == ConnectionState.CONNECTED:
                break
            elif result == ConnectionState.DISCONNECTED:
                self.restart_server()
                self.connect()
    
    def ensure_apk_exists(self):
        if not os.path.isfile(self.apk_path):
            raise ValueError(f"Provided apk path {self.apk_path} is not a valid apk")
    
    def uninstall_package(self, package):
        return sp.Popen(
            ADB_PATH,
            "uninstall",
            package
        )
    
    def list_packages(self):
        handle = sp.Popen(
            ADB_PATH,
            "shell",
            "cmd",
            "package",
            "list",
            "packages"
        ).communicate()
        result = handle.wait()
        if result != 1:
            raise IOError(f"Error connecting to device with code {result}")
        
        return 
    
    def uninstall_previous_versions(self):

    
    def full_install(self) -> bool:
        self.ensure_apk_exists()
        self.ensure_connection()
        
        self.uninstall_previous_versions()
        commands = [
            ""
        ]
        
        if self.check_connection()  
        if connection_state == DeviceState.
        if self.check_connection() != ConnectionState.CONNECTED:
            self.reconnect()

