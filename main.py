import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pynput.mouse import Controller, Button
from pynput.keyboard import Listener, KeyCode


class AutoClicker:
    def __init__(self):
        self.clicking = False
        self.mouse = Controller()
        self.click_thread = None
        self.keyboard_listener = None

        # Default settings
        self.clicks_per_second = 2
        self.click_type = "left"
        self.hotkey = "*"

        self.setup_gui()
        self.setup_hotkey_listener()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Auto Clicker")
        self.root.geometry("400x500")
        self.root.resizable(False, False)

        # Style Config
        style = ttk.Style()
        style.theme_use("clam")

        # Main Frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Title
        title_label = ttk.Label(main_frame, text="Auto Clicker", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Click type selection
        ttk.Label(main_frame, text="Click Type:").grid(row=1, column=0, sticky="w", pady=5)
        self.click_type_var = tk.StringVar(value="left")
        click_type_frame = ttk.Frame(main_frame)
        click_type_frame.grid(row=1, column=1, sticky="w", pady=5)

        ttk.Radiobutton(click_type_frame, text="Left Click", variable=self.click_type_var,
                      value="left", command=self.update_click_type).pack(side=tk.Left, padx=(0,10))
        ttk.Radiobutton(click_type_frame, text="Right Click", variable=self.click_type_var, 
                       value="right", command=self.update_click_type).pack(side=tk.LEFT)

        # Clicks per second
        ttk.Label(main_frame, text="Clicks per Second:").grid(row=2, column=0, sticky="w", pady=5)
        self.cps_var = tk.DoubleVar(value=10)
        cps_frame = ttk.Frame(main_frame)
        cps_frame.grid(row=2, column=1, sticky="w", pady=5)

        self.cps_scale = ttk.Scale(cps_frame, from_=1, to=100, variable=self.cps_var, command=self.update_cps, orient=tk.HORIZONTAL)
        self.cps_scale.pack(side=tk.LEFT, padx=(0,10), expand=True, fill=tk.X)

        self.cps_label = ttk.Label(cps_frame, text="10")
        self.cps_label.pack(side=tk.RIGHT)

        # Hotkey Configuration
        ttk.Label(main_frame, text="Toggle Hotkey:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.hotkey_var = tk.StringVar(value="*")
        hotkey_frame = ttk.Frame(main_frame)
        hotkey_frame.grid(row=3, column=1, sticky=tk.W, pady=5)

        self.hotkey_entry = ttk.Entry(hotkey_frame, textvariable=self.hotkey_var, width=5)
        self.hotkey_entry.pack(side=tk.LEFT, padx=(0,10))

        ttk.Button(hotkey_frame, text="Set", command=self.set_hotkey).pack(side=tk.LEFT)

        # Status Display
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=20)

        self.status_label = ttk.LabelFrame(status_frame, text="Stopped", font=("Arial", 12))
        self.status_label.pack()

        self.info_label = ttk.Label(status_frame, text="Press * to toggle", font=("Arial", 10))
        self.info_label.pack(pady=(5,0))

        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_clicking)
        self.start_button.pack(side=tk.LEFT, padx=(0,10))

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_clicking, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)

        # Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text="Instructions", padding="10")
        instructions_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        instructions_text = """1. Select click type (Left or Right)
2. Adjust clicks per second using the slider
3. Set your preferred hotkey (default: *)
4. Click Start or press the hotkey to toggle
5. The auto clicker will continue until stopped"""

        instructions_label = ttk.Label(instructions_frame, text=instructions_text, justify=tk.LEFT)
        instructions_label.pack()

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def update_click_type(self):
        self.click_type = self.click_type_var.get()

    def update_cps(self, value):
        try:
            self.clicks_per_second = int(float(value))
            self.cps_label.config(text=str(self.clicks_per_second))
        except (ValueError, TypeError):
            pass

    def update_hotkey(self):
        new_hotkey = self.hotkey_var.get()
        if len(new_hotkey) == 1:
            self.hotkey = new_hotkey
            self.info_label.config(text=f"Press {self.hotkey} to toggle")
            messagebox.showinfo("Hotkey Updated", f"Hotkey updated to {self.hotkey}")
        else:
            messagebox.showerror("Invalid Hotkey", "Hotkey must be a single character")
            self.hotkey_var.set(self.hotkey)

    def start_clicking(self):
        if not self.clicking:
            self.clicking = True
            self.status_label.config(text="Running", foreground="green")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            if not self.click_thread or not self.click_thread.is_alive():
                self.click_thread = threading.Thread(target=self.clicker, daemon=True)
                self.click_thread.start()

    def stop_clicking(self):
        self.clicking = False
        self.status_label.config(text="Stopped", foreground="red")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def clicker(self):
        while True:
            if self.clicking:
                if self.click_type == "left":
                    self.mouse.click(Button.left, count=1)
                else:
                    self.mouse.click(Button.right, count=1)
                
                # Calculate delay based on CPS
                delay = 1 / self.clicks_per_second
                time.sleep(delay)
            else:
                time.sleep(0.1)