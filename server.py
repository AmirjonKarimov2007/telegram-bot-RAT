from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

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

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
