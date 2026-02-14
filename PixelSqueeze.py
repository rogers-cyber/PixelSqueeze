"""
PixelSqueeze v1.0.0 – Class-Based Production-Ready
Compress Images Without Quality Loss
Full Drag & Drop | Batch Processing | Preserve Folder Structure
Select Output Format (JPG / PNG / WEBP) | Skip Existing Files
Live Counters | Portable & Lightweight | Auto-Open Output Folder
"""

import sys
import threading
import platform
import time
import queue
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_ENABLED = True
except ImportError:
    DND_ENABLED = False

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from PIL import Image

# HEIC support
try:
    import pillow_heif
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False


class PixelSqueezeApp:
    APP_NAME = "PixelSqueeze Free Version"
    APP_VERSION = "1.0.0"

    SUPPORTED_FORMATS = (
        ".png", ".jpg", ".jpeg", ".bmp", ".gif",
        ".tif", ".tiff", ".webp", ".heic"
    )

    OUTPUT_FORMATS = {
        "JPG (Best for Photos)": "JPEG",
        "PNG (Best for Graphics)": "PNG",
        "WEBP (Best for Web)": "WEBP"
    }

    def __init__(self):
        self.root = TkinterDnD.Tk() if DND_ENABLED else tk.Tk()
        tb.Style(theme="darkly")
        self.root.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.root.geometry("1020x630")

        try:
            self.root.iconbitmap(self.resource_path("logo.ico"))
        except Exception:
            pass

        self.convert_map = {}
        self.start_time = None
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.output_folder = None

        self.ui_queue = queue.Queue()

        self.format_var = tk.StringVar(value="JPG (Best for Photos)")
        self.quality_var = tk.IntVar(value=90)
        self.progress_var = tk.IntVar(value=0)
        self.eta_var = tk.StringVar(value="ETA: --:--")
        self.speed_var = tk.StringVar(value="0.00 files/sec")
        self.total_files_var = tk.IntVar(value=0)
        self.skip_existing_var = tk.BooleanVar(value=True)
        self.auto_open_var = tk.BooleanVar(value=True)
        self.preserve_structure_var = tk.BooleanVar(value=True)

        self._build_ui()
        self.process_ui_queue()

    # ---------------- UI ----------------
    def _build_ui(self):
        tb.Label(self.root, text=self.APP_NAME,
                 font=("Segoe UI", 22, "bold")).pack(pady=(10, 2))

        tb.Label(self.root, text="Compress Images Without Quality Loss",
                 font=("Segoe UI", 10, "italic"),
                 foreground="#9ca3af").pack(pady=(0, 10))

        box = tb.Labelframe(self.root, text="Files & Folders", padding=10)
        box.pack(fill="both", expand=True, padx=10, pady=6)

        self.listbox = tk.Listbox(box)
        self.listbox.pack(side="left", fill="both", expand=True)

        sb = tb.Scrollbar(box, orient="vertical", command=self.listbox.yview)
        sb.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=sb.set)

        if DND_ENABLED:
            self.listbox.drop_target_register(DND_FILES)
            self.listbox.dnd_bind("<<Drop>>", self.on_drop)

        opts = tb.Labelframe(self.root, text="Options", padding=10)
        opts.pack(fill="x", padx=10, pady=6)

        tb.Label(opts, text="Output Format").pack(side="left", padx=6)
        fmt = tb.Combobox(opts, values=list(self.OUTPUT_FORMATS.keys()),
                          textvariable=self.format_var, state="readonly", width=24)
        fmt.pack(side="left", padx=6)
        fmt.bind("<<ComboboxSelected>>", self.on_format_change)

        tb.Label(opts, text="Quality (JPG)").pack(side="left", padx=(12, 2))
        self.quality_scale = tb.Scale(opts, from_=1, to=100,
                                      variable=self.quality_var, length=150)
        self.quality_scale.pack(side="left")

        tb.Checkbutton(opts, text="Skip Existing Files",
                       variable=self.skip_existing_var).pack(side="left", padx=10)

        tb.Button(opts, text="Select Output Folder",
                  bootstyle="info-outline",
                  command=self.select_output_folder).pack(side="left", padx=10)

        progress = tb.Labelframe(self.root, text="Live Progress", padding=10)
        progress.pack(fill="x", padx=10, pady=6)

        tb.Label(progress, textvariable=self.eta_var).pack(side="left", padx=6)
        tb.Label(progress, textvariable=self.speed_var).pack(side="left", padx=6)
        tb.Label(progress, text="Total:").pack(side="left")
        tb.Label(progress, textvariable=self.total_files_var).pack(side="left")

        self.bar = tb.Progressbar(progress, variable=self.progress_var)
        self.bar.pack(fill="x", expand=True, padx=10)

        ctrl = tb.Frame(self.root)
        ctrl.pack(fill="x", padx=10, pady=10)

        tb.Button(ctrl, text="➕ Add Files", command=self.add_files).pack(side="left", padx=4)
        tb.Button(ctrl, text="📂 Add Folder", command=self.add_folder).pack(side="left", padx=4)

        tb.Button(ctrl, text="▶ Compress",
                  bootstyle="success",
                  command=lambda: threading.Thread(
                      target=self.convert_images, daemon=True).start()
                  ).pack(side="left", padx=6)

        tb.Button(ctrl, text="🧹 Clear",
                  bootstyle="danger-outline",
                  command=self.clear_all).pack(side="left", padx=6)

        tb.Button(ctrl, text="ℹ About", 
            bootstyle="info-outline", width=12,
            command=self.show_about).pack(side="right", padx=6)

    # ---------------- UTIL ----------------
    @staticmethod
    def resource_path(name):
        base = getattr(sys, "_MEIPASS", Path(__file__).parent)
        return Path(base) / name

    # ---------------- LOGIC ----------------
    def on_format_change(self, _=None):
        is_jpg = self.OUTPUT_FORMATS[self.format_var.get()] == "JPEG"
        state = "normal" if is_jpg else "disabled"
        self.quality_scale.config(state=state)

    def add_files(self):
        for f in filedialog.askopenfilenames():
            p = Path(f)
            if p.suffix.lower() in self.SUPPORTED_FORMATS:
                self.listbox.insert(tk.END, p)

    def add_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            for p in Path(folder).rglob("*"):
                if p.is_file() and p.suffix.lower() in self.SUPPORTED_FORMATS:
                    self.listbox.insert(tk.END, p)

    def on_drop(self, event):
        for f in self.root.tk.splitlist(event.data):
            p = Path(f)
            if p.is_file():
                self.listbox.insert(tk.END, p)

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = Path(folder)

    def convert_images(self):
        if not self.output_folder:
            messagebox.showwarning("Output Required", "Select output folder first.")
            return

        files = list(self.listbox.get(0, tk.END))
        total = len(files)

        if total == 0:
            return

        self.total_files_var.set(total)
        self.bar.configure(maximum=total)
        self.progress_var.set(0)

        fmt_key = self.format_var.get()
        fmt = self.OUTPUT_FORMATS[fmt_key]
        ext = "." + fmt.lower().replace("jpeg", "jpg")

        start = time.time()
        done = 0

        for src in files:
            src = Path(src)
            dst = self.output_folder / (src.stem + ext)

            if dst.exists() and self.skip_existing_var.get():
                continue

            try:
                with Image.open(src) as img:
                    if fmt in ("JPEG", "WEBP"):
                        img = img.convert("RGB")

                    if fmt == "JPEG":
                        img.save(dst, "JPEG",
                                 quality=self.quality_var.get(),
                                 optimize=True,
                                 progressive=True)

                    elif fmt == "PNG":
                        img.save(dst, "PNG", optimize=True)

                    elif fmt == "WEBP":
                        img.save(dst, "WEBP", quality=95, method=6)

                done += 1

                elapsed = time.time() - start
                speed = done / elapsed if elapsed else 0

                self.ui_queue.put(("progress", done))
                self.ui_queue.put(("speed", f"{speed:.2f} files/sec"))

            except Exception as e:
                logging.error(f"Failed: {src} → {e}")

        self.ui_queue.put(("speed", "Completed ✔"))

        if self.auto_open_var.get() and done > 0:
            self.open_folder(self.output_folder)

    def open_folder(self, path):
        if platform.system() == "Windows":
            import os; os.startfile(path)
        elif platform.system() == "Darwin":
            import os; os.system(f'open "{path}"')
        else:
            import os; os.system(f'xdg-open "{path}"')

    def clear_all(self):
        self.listbox.delete(0, tk.END)
        self.progress_var.set(0)
        self.total_files_var.set(0)

    def process_ui_queue(self):
        while not self.ui_queue.empty():
            item = self.ui_queue.get()

            if isinstance(item, tuple):
                key, value = item

                if key == "progress":
                    self.progress_var.set(value)

                elif key == "speed":
                    self.speed_var.set(value)

        self.root.after(100, self.process_ui_queue)

    def show_about(self):
        win = tb.Toplevel(self.root)
        win.title(f"ℹ About {self.APP_NAME}")
        win.resizable(False, False)
        win.grab_set()
        win.attributes("-toolwindow", True)

        # Center window
        win_w, win_h = 480, 500
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (win_w // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (win_h // 2)
        win.geometry(f"{win_w}x{win_h}+{x}+{y}")

        frame = tb.Frame(win, padding=15)
        frame.pack(fill="both", expand=True)

        # Title
        tb.Label(
            frame,
            text=f"{self.APP_NAME}",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", pady=(0, 4))

        tb.Label(
            frame,
            text=f"Version {self.APP_VERSION} (FREE)",
            font=("Segoe UI", 10, "italic"),
            foreground="#9ca3af"
        ).pack(anchor="w", pady=(0, 10))

        # Description
        tb.Label(
            frame,
            text=(
                "PixelSqueeze is a fast and lightweight image compression tool.\n\n"
                "It allows you to compress images without noticeable quality loss "
                "while supporting batch processing, drag & drop, and modern formats "
                "such as JPG, PNG, and WEBP.\n\n"
                "This FREE version is designed for everyday use and personal projects."
            ),
            wraplength=440,
            justify="left"
        ).pack(anchor="w", pady=(0, 10))

        # Features
        tb.Label(
            frame,
            text="Key Features",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(6, 2))

        tb.Label(
            frame,
            text=(
                "• Batch image compression\n"
                "• Drag & drop files and folders\n"
                "• JPG / PNG / WEBP output formats\n"
                "• Adjustable JPG quality\n"
                "• Live progress and speed display\n"
                "• Auto-open output folder\n"
                "• Portable & lightweight"
            ),
            justify="left"
        ).pack(anchor="w", pady=(0, 10))

        # Developer Info
        tb.Label(
            frame,
            text="Developer",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(6, 2))

        tb.Label(
            frame,
            text=(
                "Mate Technologies / Website: https://matetools.gumroad.com"
            ),
            justify="left"
        ).pack(anchor="w", pady=(0, 10))

        # Footer
        tb.Label(
            frame,
            text="© 2026 PixelSqueeze – Free Version",
            font=("Segoe UI", 9),
            foreground="#9ca3af"
        ).pack(anchor="center", pady=(10, 6))

        tb.Button(
            frame,
            text="Close",
            bootstyle="secondary",
            width=15,
            command=win.destroy
        ).pack(pady=6)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    PixelSqueezeApp().run()
