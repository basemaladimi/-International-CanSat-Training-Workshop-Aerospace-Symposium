import tkinter as tk
from tkinter import ttk
import serial
import re
import threading
import time
import urllib.request
from PIL import Image, ImageTk
import io
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import webview  # pip install pywebview

SERIAL_PORT = "COM4"
BAUD_RATE = 115200
CAMERA_WEB_URL = "http://192.168.4.1/"  # Use the ESP32-CAM web interface page!

BUFFER_SIZE = 50

def parse_sensor_data(text):
    result = {}
    m = re.search(r'Accel \(m/s²\): ([\d\.\-]+), ([\d\.\-]+), ([\d\.\-]+)', text)
    if m: result["ax"], result["ay"], result["az"] = map(float, m.groups())
    m = re.search(r'Gyro \(°/s\): ([\d\.\-]+), ([\d\.\-]+), ([\d\.\-]+)', text)
    if m: result["gx"], result["gy"], result["gz"] = map(float, m.groups())
    m = re.search(r'Temp: ([\d\.\-]+)', text)
    if m: result["Temp"] = float(m.group(1))
    m = re.search(r'Press: ([\d\.\-]+)', text)
    if m: result["Press"] = float(m.group(1))
    m = re.search(r'Alt: ([\d\.\-]+)', text)
    if m: result["Alt"] = float(m.group(1))
    m = re.search(r'GPS -> Lat: ([\d\.\-]+), Lon: ([\d\.\-]+), Sats: (\d+)', text)
    if m: result["GPS_Lat"], result["GPS_Lon"], result["GPS_Sats"] = float(m.group(1)), float(m.group(2)), int(m.group(3))
    return result

accel_buffer = {"ax": [], "ay": [], "az": []}
gyro_buffer = {"gx": [], "gy": [], "gz": []}
alt_buffer = []
orientation_buffer = {"gx": 0, "gy": 0, "gz": 0}
latest_readings = {
    "Temp": "--", "Press": "--", "Alt": "--", "GPS_Lat": "--", "GPS_Lon": "--", "GPS_Sats": "--",
    "ax": "--", "ay": "--", "az": "--", "gx": "--", "gy": "--", "gz": "--"
}

class SensorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Sensor & Camera Dashboard")
        self.root.geometry("1800x1100")
        self.root.configure(bg="white")

        # ----------- Title Section -----------
        title_frame = tk.Frame(root, bg="white")
        title_frame.pack(side=tk.TOP, fill=tk.X, pady=(15, 0))
        title_label = tk.Label(
            title_frame,
            text="ICESCO’s 4th International CanSat Training Workshop & Aerospace Symposium",
            font=("Arial Rounded MT Bold", 32),
            bg="white",
            fg="#0052cc"
        )
        title_label.pack(pady=(0, 5))
        team_label = tk.Label(
            title_frame,
            text="Team: ICESCO SatRiders 2.0",
            font=("Arial Rounded MT Bold", 22),
            bg="white",
            fg="#0052cc"
        )
        team_label.pack(pady=(0, 15))

        # ----------------- Top Section -----------------
        top_frame = tk.Frame(root, bg="white")
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Camera (left, larger)
        cam_frame = tk.Frame(top_frame, bg="white")
        cam_frame.pack(side=tk.LEFT, padx=10)
        self.camera_width = 400
        self.camera_height = 300

        # Instead of camera_label, use a button to open the webview
        self.camera_webview_button = tk.Button(
            cam_frame,
            text="Open Camera Video Stream",
            font=("Arial", 16, "bold"),
            width=32,
            height=12,
            bg="#e6e6e6",
            fg="#0052cc",
            command=self.open_camera_webview
        )
        self.camera_webview_button.pack()

        self.webview_window_shown = False

        # Sensor values (middle, centered, vertical)
        sensor_val_frame = tk.Frame(top_frame, bg="white")
        sensor_val_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.temp_var = tk.StringVar(value="--")
        self.press_var = tk.StringVar(value="--")
        self.alt_var = tk.StringVar(value="--")
        self.sats_var = tk.StringVar(value="--")

        sensor_val_frame.columnconfigure(0, weight=1)
        for i in range(8):
            sensor_val_frame.rowconfigure(i, weight=1)

        temp_label = tk.Label(sensor_val_frame, text="Temperature (°C):", font=("Arial", 20), bg="white")
        temp_label.grid(row=0, column=0, sticky="ew", pady=(25, 0))
        temp_val_label = tk.Label(sensor_val_frame, textvariable=self.temp_var, font=("Arial", 24, "bold"), bg="white")
        temp_val_label.grid(row=1, column=0, sticky="ew")

        press_label = tk.Label(sensor_val_frame, text="Pressure (hPa):", font=("Arial", 20), bg="white")
        press_label.grid(row=2, column=0, sticky="ew", pady=(15, 0))
        press_val_label = tk.Label(sensor_val_frame, textvariable=self.press_var, font=("Arial", 24, "bold"), bg="white")
        press_val_label.grid(row=3, column=0, sticky="ew")

        alt_label = tk.Label(sensor_val_frame, text="Altitude (m):", font=("Arial", 20), bg="white")
        alt_label.grid(row=4, column=0, sticky="ew", pady=(15, 0))
        alt_val_label = tk.Label(sensor_val_frame, textvariable=self.alt_var, font=("Arial", 24, "bold"), bg="white")
        alt_val_label.grid(row=5, column=0, sticky="ew")

        sats_label = tk.Label(sensor_val_frame, text="GPS Sats:", font=("Arial", 20), bg="white")
        sats_label.grid(row=6, column=0, sticky="ew", pady=(15, 0))
        sats_val_label = tk.Label(sensor_val_frame, textvariable=self.sats_var, font=("Arial", 24, "bold"), bg="white")
        sats_val_label.grid(row=7, column=0, sticky="ew")

        # Orientation (right, cylinder larger)
        orient_frame = tk.Frame(top_frame, bg="white")
        orient_frame.pack(side=tk.RIGHT, padx=10)
        self.fig3d = plt.figure(figsize=(6, 5), facecolor='white')
        self.ax3d = self.fig3d.add_subplot(111, projection='3d', facecolor='white')
        self.canvas3d = FigureCanvasTkAgg(self.fig3d, master=orient_frame)
        self.canvas3d.get_tk_widget().pack()
        self.update_3d_cylinder()

        # ----------------- Middle Section -----------------
        mid_frame = tk.Frame(root, bg="white")
        mid_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Altitude graph (left, larger)
        alt_graph_frame = tk.Frame(mid_frame, bg="white")
        alt_graph_frame.pack(side=tk.LEFT, padx=60)
        self.fig_alt, self.ax_alt = plt.subplots(figsize=(5, 3), facecolor='white')
        self.ax_alt.set_facecolor('white')
        self.alt_line, = self.ax_alt.plot([], [], 'b', label="Altitude")
        self.ax_alt.set_title("Altitude (m)")
        self.ax_alt.set_xlabel("Sample")
        self.ax_alt.set_ylabel("Altitude")
        self.ax_alt.set_ylim(0, 500)
        self.ax_alt.legend()
        self.canvas_alt = FigureCanvasTkAgg(self.fig_alt, master=alt_graph_frame)
        self.canvas_alt.get_tk_widget().pack()

        # Acceleration graph (center, larger)
        accel_graph_frame = tk.Frame(mid_frame, bg="white")
        accel_graph_frame.pack(side=tk.LEFT, padx=90)
        self.fig_accel, self.ax_accel = plt.subplots(figsize=(5, 3), facecolor='white')
        self.ax_accel.set_facecolor('white')
        self.accel_lines = self.ax_accel.plot([], [], 'r', [], [], 'g', [], [], 'b')
        self.ax_accel.set_title("Acceleration (ax, ay, az)")
        self.ax_accel.set_xlabel("Sample")
        self.ax_accel.set_ylabel("Accel (m/s²)")
        self.ax_accel.set_ylim(-10, 10)
        self.ax_accel.legend(["ax", "ay", "az"])
        self.canvas_accel = FigureCanvasTkAgg(self.fig_accel, master=accel_graph_frame)
        self.canvas_accel.get_tk_widget().pack()

        # Gyro graph (right, larger)
        gyro_graph_frame = tk.Frame(mid_frame, bg="white")
        gyro_graph_frame.pack(side=tk.LEFT, padx=90)
        self.fig_gyro, self.ax_gyro = plt.subplots(figsize=(5, 3), facecolor='white')
        self.ax_gyro.set_facecolor('white')
        self.gyro_lines = self.ax_gyro.plot([], [], 'r', [], [], 'g', [], [], 'b')
        self.ax_gyro.set_title("Gyro (gx, gy, gz)")
        self.ax_gyro.set_xlabel("Sample")
        self.ax_gyro.set_ylabel("Gyro (°/s)")
        self.ax_gyro.set_ylim(-10, 10)
        self.ax_gyro.legend(["gx", "gy", "gz"])
        self.canvas_gyro = FigureCanvasTkAgg(self.fig_gyro, master=gyro_graph_frame)
        self.canvas_gyro.get_tk_widget().pack()

        # ----------------- Bottom Section -----------------
        bottom_frame = tk.Frame(root, bg="white")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        table_columns = [
            "Temp", "Press", "Alt", "GPS_Lat", "GPS_Lon", "GPS_Sats",
            "ax", "ay", "az", "gx", "gy", "gz"
        ]
        self.val_labels = {}
        for i, col in enumerate(table_columns):
            tk.Label(bottom_frame, text=col, font=("Arial", 14, "bold"), relief=tk.RIDGE, width=12, bg="white").grid(row=0, column=i, sticky="nsew")
            self.val_labels[col] = tk.Label(bottom_frame, text="--", font=("Arial", 14), relief=tk.RIDGE, width=12, bg="white")
            self.val_labels[col].grid(row=1, column=i, sticky="nsew")

        # ---------------- Serial Thread ----------------
        self.serial_connected = False
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            time.sleep(2)
            self.serial_connected = True
        except Exception as e:
            print(f"Serial connection error: {e}")
            self.ser = None

        self.running = True
        threading.Thread(target=self.read_serial, daemon=True).start()
        self.update_graphs()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def open_camera_webview(self):
        # Only open one camera webview window
        if hasattr(self, 'webview_thread') and self.webview_thread.is_alive():
            # Already running
            return

        def run_webview():
            # This is blocking, so run in a thread
            webview.create_window("ESP32-CAM Live Stream", CAMERA_WEB_URL, width=480, height=360, resizable=True)

        self.webview_thread = threading.Thread(target=run_webview, daemon=True)
        self.webview_thread.start()

    def read_serial(self):
        while self.running and self.serial_connected:
            try:
                if self.ser.in_waiting:
                    text = self.ser.read(self.ser.in_waiting).decode("utf-8", errors="ignore")
                    blocks = text.split("-----------------------")
                    for block in blocks:
                        if "SENSOR DATA" in block or "RECEIVED SENSOR DATA" in block:
                            data = parse_sensor_data(block)
                            if data:
                                for key in latest_readings:
                                    if key in data:
                                        latest_readings[key] = f"{data[key]:.2f}" if isinstance(data[key], float) else str(data[key])
                                if "Temp" in data:
                                    self.temp_var.set(f"{data['Temp']:.2f}")
                                if "Press" in data:
                                    self.press_var.set(f"{data['Press']:.2f}")
                                if "Alt" in data:
                                    self.alt_var.set(f"{data['Alt']:.2f}")
                                    alt_buffer.append(data["Alt"])
                                    if len(alt_buffer) > BUFFER_SIZE:
                                        alt_buffer.pop(0)
                                if "GPS_Sats" in data:
                                    self.sats_var.set(str(data["GPS_Sats"]))
                                for k in ["ax", "ay", "az"]:
                                    if k in data:
                                        accel_buffer[k].append(data[k])
                                        if len(accel_buffer[k]) > BUFFER_SIZE:
                                            accel_buffer[k].pop(0)
                                for k in ["gx", "gy", "gz"]:
                                    if k in data:
                                        gyro_buffer[k].append(data[k])
                                        orientation_buffer[k] = data[k]
                                        if len(gyro_buffer[k]) > BUFFER_SIZE:
                                            gyro_buffer[k].pop(0)
            except Exception as e:
                print(f"Serial read error: {e}")
            time.sleep(0.1)

    def update_graphs(self):
        xalt = list(range(len(alt_buffer)))
        self.alt_line.set_data(xalt, alt_buffer)
        self.ax_alt.set_xlim(0, max(BUFFER_SIZE, len(alt_buffer)))
        self.canvas_alt.draw()

        xaccel = list(range(len(accel_buffer["ax"])))
        for i, k in enumerate(["ax", "ay", "az"]):
            self.accel_lines[i].set_data(xaccel, accel_buffer[k])
        self.ax_accel.set_xlim(0, max(BUFFER_SIZE, len(xaccel)))
        self.canvas_accel.draw()

        xgyro = list(range(len(gyro_buffer["gx"])))
        for i, k in enumerate(["gx", "gy", "gz"]):
            self.gyro_lines[i].set_data(xgyro, gyro_buffer[k])
        self.ax_gyro.set_xlim(0, max(BUFFER_SIZE, len(xgyro)))
        self.canvas_gyro.draw()

        for key, label in self.val_labels.items():
            label.config(text=latest_readings.get(key, "--"), bg="white")

        self.root.after(100, self.update_graphs)

    def update_3d_cylinder(self):
        self.ax3d.cla()
        z = np.linspace(-0.5, 0.5, 50)
        theta = np.linspace(0, 2 * np.pi, 50)
        Z, THETA = np.meshgrid(z, theta)
        RADIUS = 0.4
        X = RADIUS * np.cos(THETA)
        Y = RADIUS * np.sin(THETA)
        gx, gy, gz = orientation_buffer["gx"], orientation_buffer["gy"], orientation_buffer["gz"]
        theta_x = np.radians(gx)
        theta_y = np.radians(gy)
        theta_z = np.radians(gz)
        Rx = np.array([[1,0,0],[0,np.cos(theta_x),-np.sin(theta_x)],[0,np.sin(theta_x),np.cos(theta_x)]])
        Ry = np.array([[np.cos(theta_y),0,np.sin(theta_y)],[0,1,0],[-np.sin(theta_y),0,np.cos(theta_y)]])
        Rz = np.array([[np.cos(theta_z),-np.sin(theta_z),0],[np.sin(theta_z),np.cos(theta_z),0],[0,0,1]])
        R = Rz @ Ry @ Rx
        points = np.stack([X.flatten(), Y.flatten(), Z.flatten()], axis=1)
        rotated = points @ R.T
        Xr = rotated[:, 0].reshape(X.shape)
        Yr = rotated[:, 1].reshape(Y.shape)
        Zr = rotated[:, 2].reshape(Z.shape)
        self.ax3d.plot_surface(Xr, Yr, Zr, color='white', edgecolor='k', alpha=0.7)
        self.ax3d.set_title("Orientation (Cylinder)", color="black")
        self.ax3d.set_xlim(-0.6, 0.6)
        self.ax3d.set_ylim(-0.6, 0.6)
        self.ax3d.set_zlim(-0.6, 0.6)
        self.ax3d.set_box_aspect([1,1,1])
        self.ax3d.set_facecolor('white')
        self.canvas3d.draw()
        self.root.after(100, self.update_3d_cylinder)

    def on_close(self):
        self.running = False
        if self.ser:
            self.ser.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorApp(root)
    root.mainloop()
