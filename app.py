import threading
import ctypes
import server  # Сервер
import gui     # Интерфейс

# Регистрируем отдельный ID приложения для Windows, чтобы работала иконка в Пуске
try:
    myappid = 'flowseal.webmouse.server.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

if __name__ == '__main__':
    server_thread = threading.Thread(target=server.run_flask)
    server_thread.daemon = True
    server_thread.start()

    gui.setup_gui()
