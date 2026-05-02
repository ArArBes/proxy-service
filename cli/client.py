import json
from threading import Thread
from tkinter import Tk, Label, Button, Entry, messagebox, DISABLED, NORMAL

from websocket import WebSocketApp
from requests import post

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VM Client")
        self.root.geometry("400x250")
        self.base_url = "http://localhost:81"
        self.ws_url = "ws://localhost:81/ws/status/"

        Label(root, text="Ключ активации:").pack(pady=5)
        self.key_entry = Entry(root, width=50)
        self.key_entry.pack(pady=5)
        self.key_entry.focus()

        self.connect_btn = Button(root, text="Подключиться", command=self.activate)
        self.connect_btn.pack(pady=5)

        self.disconnect_btn = Button(root, text="Отключиться", command=self.disconnect, state=DISABLED)
        self.disconnect_btn.pack(pady=5)

        self.status_label = Label(root, text="Статус: не подключён", fg="gray")
        self.status_label.pack(pady=10)

        self.vm_data = None
        self.user_id = None
        self.ws = None

        root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _log(self, text, color="blue"):
        self.status_label.config(text=f"Статус: {text}", fg=color)

    def activate(self):
        key = self.key_entry.get().strip()
        if not key:
            messagebox.showerror("Ошибка", "Введите ключ")
            return

        self.connect_btn.config(state=DISABLED, text="Подключение")
        self._log("Отправка ключа", "orange")

        try:
            resp = post(f"{self.base_url}/api/activate-key/",
                        json={"activation_key": key}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                self.vm_data = {
                    "host": data["host"],
                    "port": data["port"],
                    "protocol": data["protocol"]
                }
                self.user_id = data.get("user_id")
                self._log("Ключ принят, открываем WebSocket", "orange")
                self._connect_ws()
            else:
                err = resp.json().get("detail", "Ошибка активации")
                self._log(err, "red")
                self.connect_btn.config(state=NORMAL, text="Подключиться")
        except Exception as e:
            self._log(f"Ошибка: {e}", "red")
            self.connect_btn.config(state=NORMAL, text="Подключиться")

    def _connect_ws(self):
        if not self.user_id:
            self._log("Нет user_id", "red")
            return
        ws_url = f"{self.ws_url}{self.user_id}/"
        self.ws = WebSocketApp(ws_url,
                               on_open=self._on_open,
                               on_message=self._on_message,
                               on_error=self._on_error,
                               on_close=self._on_close)
        Thread(target=self.ws.run_forever, daemon=True).start()

    def disconnect(self):
        if self.ws and self.ws.sock and self.ws.sock.connected:
            self.ws.send(json.dumps({"action": "disconnect"}))
            self._log("Отключение", "orange")

    def _on_open(self, ws):
        self.root.after(0, lambda: self._log("Ожидание статуса", "orange"))
        self.root.after(0, lambda: self.disconnect_btn.config(state=NORMAL))

    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
            status = data.get("status")
            msg = data.get("message")
            if status == "connected":
                if self.vm_data:
                    self.root.after(0, lambda: self._log(
                        f"Подключено к {self.vm_data['host']}:{self.vm_data['port']} ({self.vm_data['protocol']})",
                        "green"))
                    self.root.after(0, lambda: self.disconnect_btn.config(state=NORMAL))
                else:
                    self.root.after(0, lambda: self._log("Подключено", "green"))
            elif status == "no_free_vms":
                self.root.after(0, lambda: self._log("Нет свободных прокси", "red"))
                self.root.after(0, lambda: self.connect_btn.config(state=NORMAL, text="Подключиться"))
            elif status == "disconnected":
                self.root.after(0, lambda: self._log(f"Отключено: {msg}", "gray"))
                self.root.after(0, lambda: self.connect_btn.config(state=NORMAL, text="Подключиться"))
                self.root.after(0, lambda: self.disconnect_btn.config(state=DISABLED))
            else:
                self.root.after(0, lambda: self._log(f"Статус: {status}", "blue"))
        except:
            pass

    def _on_error(self, ws, error):
        self.root.after(0, lambda: self._log(f"WebSocket ошибка: {error}", "red"))
        self.root.after(0, lambda: self.connect_btn.config(state=NORMAL, text="Подключиться"))
        self.root.after(0, lambda: self.disconnect_btn.config(state=DISABLED))

    def _on_close(self, ws, close_status_code=None, close_msg=None):
        self.root.after(0, lambda: self._log("Соединение закрыто", "gray"))
        self.root.after(0, lambda: self.connect_btn.config(state=NORMAL, text="Подключиться"))
        self.root.after(0, lambda: self.disconnect_btn.config(state=DISABLED))

if __name__ == "__main__":
    root = Tk()
    app = ClientApp(root)
    root.mainloop()