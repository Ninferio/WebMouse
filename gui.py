import os
import sys
import socket
import threading
import tkinter as tk
import pystray
from PIL import Image, ImageTk
import qrcode  # Добавляем библиотеку для QR
import server

if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

root = None
icon = None

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0] # Исправлено получение строки IP
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()
CONNECT_URL = f"http://{LOCAL_IP}:5000"

def toggle_server(status_label, btn):
    server.server_active = not server.server_active
    if server.server_active:
        status_label.config(text="СТАТУС: Сервер работает", fg="#00cbc6")
        btn.config(text="Отключить сервер", bg="#d9534f")
        btn.default_bg = "#d9534f"
        btn.hover_bg = "#b53f3b"
    else:
        status_label.config(text="СТАТУС: Сервер остановлен", fg="#ff4a4a")
        btn.config(text="Включить сервер", bg="#5cb85c")
        btn.default_bg = "#5cb85c"
        btn.hover_bg = "#4cae4c"

def hide_to_tray():
    global root
    root.withdraw()

def show_window(icon_instance, item):
    global root
    icon_instance.stop()
    root.after(0, root.deiconify)

def on_exit():
    global icon, root
    if icon:
        icon.stop()
    if root:
        root.destroy()
    os._exit(0)

def run_pystray():
    global icon
    icon_path = os.path.join(base_dir, 'icon.png')
    if os.path.exists(icon_path):
        image = Image.open(icon_path)
    else:
        image = Image.new('RGB', (64, 64), color=(0, 203, 198))

    menu = pystray.Menu(
        pystray.MenuItem('Открыть настройки', show_window, default=True),
        pystray.MenuItem('Выход', on_exit)
    )
    icon = pystray.Icon("WebMouse", image, "WebMouse", menu)
    icon.run()

def on_closing_window():
    hide_to_tray()
    threading.Thread(target=run_pystray, daemon=True).start()

def copy_to_clipboard(info_lbl):
    global root
    root.clipboard_clear()
    root.clipboard_append(CONNECT_URL)
    info_lbl.config(text="Ссылка скопирована в буфер!", fg="#00cbc6")
    root.after(2000, lambda: info_lbl.config(text="Наведите камеру смартфона на QR-код:", fg="#888"))

def add_hover(btn, default_bg, hover_bg):
    btn.default_bg = default_bg
    btn.hover_bg = hover_bg
    btn.bind("<Enter>", lambda e: btn.config(bg=btn.hover_bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=btn.default_bg))

def setup_gui():
    global root
    root = tk.Tk()
    root.title("WebMouse Server v1.1")
    root.geometry("450x420") # Немного увеличили высоту окна под QR-код
    root.configure(bg="#1e1e1e")
    root.resizable(False, False)

    icon_path = os.path.join(base_dir, 'icon.png')
    if os.path.exists(icon_path):
        try:
            img = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, img)
        except Exception:
            pass

    title_lbl = tk.Label(root, text="Управление Веб-Мышью", font=("Arial", 16, "bold"), bg="#1e1e1e", fg="white")
    title_lbl.pack(pady=15)

    info_lbl = tk.Label(root, text="Наведите камеру смартфона на QR-код:", font=("Arial", 11), bg="#1e1e1e", fg="#888")
    info_lbl.pack(pady=(0, 5))

    # --- СЕКЦИЯ ГЕНЕРАЦИИ И ВЫВОДА QR-КОДА ---
    # Генерируем QR-код в цветах нашего интерфейса (темно-серый и бирюзовый)
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(CONNECT_URL)
    qr.make(fit=True)
    
    # Красим QR-код под стиль приложения: фон темно-серый (#2d2d2d), сам код бирюзовый (#00cbc6)
    qr_img = qr.make_image(fill_color="#00cbc6", back_color="#2d2d2d")
    
    # Превращаем картинку PIL в формат, который понимает Tkinter
    tk_qr_img = ImageTk.PhotoImage(image=qr_img)

    # Кликая на QR-код, пользователь всё еще может скопировать текстовую ссылку
    qr_label = tk.Label(root, image=tk_qr_img, bg="#1e1e1e", cursor="hand2")
    qr_label.image = tk_qr_img  # Защита от удаления картинки сборщиком мусора
    qr_label.pack(pady=10)
    qr_label.bind("<Button-1>", lambda e: copy_to_clipboard(info_lbl))
    # -----------------------------------------

    status_lbl = tk.Label(root, text="СТАТУС: Сервер работает", font=("Arial", 11, "bold"), bg="#1e1e1e", fg="#00cbc6")
    status_lbl.pack(pady=15)

    toggle_btn = tk.Button(root, text="Отключить сервер", font=("Arial", 10, "bold"), bg="#d9534f", fg="white", 
                           bd=0, padx=25, pady=8, activebackground="#b53f3b", activeforeground="white", cursor="hand2",
                           command=lambda: toggle_server(status_lbl, toggle_btn))
    toggle_btn.pack(pady=5)
    
    add_hover(toggle_btn, "#d9534f", "#b53f3b")

    root.protocol("WM_DELETE_WINDOW", on_closing_window)
    root.mainloop()
