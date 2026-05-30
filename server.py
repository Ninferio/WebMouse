import os
import sys
import logging
from flask import Flask, jsonify, request
import pyautogui

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

static_folder_path = os.path.join(base_dir, 'static')
flask_app = Flask(__name__, static_folder=static_folder_path, static_url_path='/static')

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

server_active = True

@flask_app.route('/')
def index():
    if not server_active:
        return "Сервер отключен администратором", 503
    return flask_app.send_static_file('index.html')

@flask_app.route('/move_mouse')
def move_mouse():
    if not server_active:
        return jsonify(success=False), 503
    dx = float(request.args.get('dx', 0))
    dy = float(request.args.get('dy', 0))
    sensitivity = 2.0 
    pyautogui.moveRel(dx * sensitivity, dy * sensitivity)
    return jsonify(success=True)

@flask_app.route('/click')
def click():
    if not server_active:
        return jsonify(success=False), 503
    button = request.args.get('b', 'left')
    pyautogui.click(button=button)
    return jsonify(success=True)

# НОВАЯ ФУНКЦИЯ: Обработка скролла (колёсика мыши)
@flask_app.route('/scroll')
def scroll():
    if not server_active:
        return jsonify(success=False), 503
    clicks = int(request.args.get('clicks', 0))
    # pyautogui.scroll принимает положительные (вверх) или отрицательные (вниз) числа
    # Множитель 40-70 ускоряет прокрутку, чтобы не крутить пальцем бесконечно
    pyautogui.scroll(clicks * 50)
    return jsonify(success=True)

def run_flask():
    flask_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
