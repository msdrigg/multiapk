import os

import subprocess as sp
import re
import warnings
from enum import Enum

from constants import ADB_PATH, IP_MATCHER


class DeviceState(Enum):
    CONNECTED = "device"
    DISCONNECTED = "offline"
    UNAUTHORIZED = "unauthorized"


class Installer:
    def __init__(self, ip_address, apk_path):
        super()
        if IP_MATCHER.match(ip_address):
            warnings.warn(
                f"Cannot create installer with invalid ip adderss: {ip_address}"
            )
        self.ip_address = ip_address
        self.call_flag = ["-s", ip_address]
        self.device_state = DeviceState.DISCONNECTED
        self.apk_path = apk_path

    def connect(self) -> sp.Popen:
        return sp.Popen(
            ADB_PATH,
            "connect",
            self.ip_address,
            stdout=sp.PIPE
        )

    def check_connection(self) -> DeviceState:
        handle = sp.Popen(
            ADB_PATH,
            "devices",
            stdout=sp.PIPE
        )

        acceptable_devices = [
            device for device in handle.stdout.readline if device.startswith(self.ip_address)
        ]
        
        if handle.wait() != 1:
            warnings.warn("Error checking device connection")
        
        if len(acceptable_devices) == 0:
            return DeviceState.DISCONNECTED
        elif len(acceptable_devices) > 1:
            warnings.warn(
                "Error checking if installer is connected because "
                f"more than one device matched:\n{'\n'.join(acceptable_devices)}"
            )
            return DeviceState.DISCONNECTED
        else:
            state_string = acceptable_devices.split()[1].upper()
            if state_string not in DeviceState:
                warnings.warn(f"Unexpected state received from `adb devices': {state_string}")
            return DeviceState.get(
                state_string,
                DeviceState.DISCONNECTED
            )
    
    def reconnect(self):
        self.disconnect_all()
        return self.connect()
    
    def disconnect_all(self):
        disconnect_code = self.disconnect_all().wait()
        if disconnect_code != 1:
            warnings.warn(
                f"Getting error disconnecting from device {disconnect_code}"
            )

    def restart_server(self):
        self.kill_server()

        start_result = sp.Popen(
            ADB_PATH,
            "start-server"
        )
        if start_result != 1:
            warnings.warn(
                f"Error starting server with exit code {start_result}"
            )
        
    def kill_server(self):
        kill_result = sp.Popen(
            ADB_PATH,
            "kill-server"
        ).wait()

        if kill_result != 1:
            warnings.warn(
                f"Error killing server with error code {kill_result}"
            )
    
    def ensure_connection(self):
        # Starts an event loop to make sure the device is connected
        while True:
            handle = self.connect()
            
            result = self.check_connection()
            if result == DeviceState.CONNECTED:
                break
            elif result == DeviceState.DISCONNECTED:
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
        if self.check_connection() != DeviceState.CONNECTED:
            self.reconnect()

