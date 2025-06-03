import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import json

class BluetoothApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Control Bluetooth")
        self.root.geometry("500x400")
        self.serial_port = None
        self.running = False

        # Colores
        bg_color = "#2d2d2d"
        fg_color = "#f0f0f0"
        accent_color = "#3e3e3e"

        # Fuente común
        font_big = ("Candara", 14)

        # Fondo de la ventana
        self.root.configure(bg=bg_color)

        # Estilos ttk
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TLabel", background=bg_color, foreground=fg_color, font=font_big)
        style.configure("TButton", background=accent_color, foreground=fg_color, font=font_big)
        style.map("TButton", background=[('active', '#505050')])
        style.configure("TCombobox", fieldbackground=accent_color, background=accent_color, foreground=fg_color)

        ttk.Label(root, text="Puerto COM:").pack(pady=10)

        self.port_combo = ttk.Combobox(root, values=self.get_ports(), font=font_big, width=30)
        self.port_combo.pack(pady=5)

        self.connect_button = ttk.Button(root, text="Conectar", command=self.connect)
        self.connect_button.pack(pady=10, ipadx=10, ipady=5)

        self.on_button = ttk.Button(root, text="Encender", command=lambda: self.send_command(1), state='disabled')
        self.on_button.pack(pady=10, ipadx=10, ipady=5)

        self.off_button = ttk.Button(root, text="Apagar", command=lambda: self.send_command(2), state='disabled')
        self.off_button.pack(pady=10, ipadx=10, ipady=5)

        ttk.Label(root, text="Valor potenciómetro:").pack(pady=10)

        self.value_label = ttk.Label(root, text="---", font=("Arial", 24), foreground="cyan", background=bg_color)
        self.value_label.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def get_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def connect(self):
        port = self.port_combo.get()
        if not port:
            messagebox.showwarning("Advertencia", "Seleccione un puerto COM.")
            return
        try:
            self.serial_port = serial.Serial(port, 9600, timeout=1)
            self.running = True
            threading.Thread(target=self.read_data, daemon=True).start()
            self.on_button['state'] = 'normal'
            self.off_button['state'] = 'normal'
            self.connect_button['state'] = 'disabled'
            self.port_combo['state'] = 'disabled'
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar: {e}")

    def send_command(self, command):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(f"{command}\n".encode())

    def read_data(self):
        while self.running and self.serial_port:
            try:
                line = self.serial_port.readline().decode().strip()
                if line.startswith("{") and line.endswith("}"):
                    data = json.loads(line)
                    pot_value = data.get("potenciometro", "---")
                    self.value_label.config(text=str(pot_value))
            except Exception:
                continue

    def close(self):
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = BluetoothApp(root)
    root.mainloop()