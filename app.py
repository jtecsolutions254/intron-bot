from flask import Flask, request, jsonify
from flask import Flask, render_template, request, jsonify

from threading import Thread
from bot import run_bot

app = Flask(__name__)
thread = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    global thread
    data = request.get_json()
    lang = data.get('language', 'sw')
    if thread and thread.is_alive():
        return jsonify({"status": "already running", "language": lang})
    thread = Thread(target=run_bot, args=(lang,), daemon=True)
    thread.start()
    return jsonify({"status": "started", "language": lang})

if __name__ == '__main__':
    import os

port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port, debug=True)
