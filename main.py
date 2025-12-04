import os 
import sys
import shutil # To copy files and check system PATH
import stat # To change file permissions (chmod +x for Linux/Mac)
import platform #To detect the operating system
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import yt_dlp
import imageio_ffmpeg # The library containing the FFmpeg binary

class MyTubeDownloader:

    def __init__(self, root):
        self.root = root
        self.root.title("MyTube Downloader")
        self.root.geometry("520x620")
        self.root.resizable(False, False)

        # --- Variables ---
        self.video_url = tk.StringVar()
        self.download_path = tk.StringVar()
        self.format_choice = tk.StringVar(value="mp4")
        self.video_title = tk.StringVar()
        self.quality_choice = tk.StringVar()

        # State Flags
        self.downloading = False
        self.cancelled = False
        self.ydl = None

        # 1. FFmpeg Setup (Hybrid Approach: System -> Local -> ImageIO)
        self.ffmpeg_path = self.check_and_setup_ffmpeg()

        # 2. Auto-Update Check (Runs in a Background Thread)
        threading.Thread(target=self.auto_update_ytdlp, daemon=True).start()

        self.create_widgets()

    def check_and_setup_ffmpeg(self):
        """
        Priority 1: Checks if FFmpeg is installed globally on the system (PATH).
        Priority 2: Checks if FFmpeg exists in the local app directory.
        Priority 3: Extracts it from imageio_ffmpeg and installs it locally.
        """
        print("[System] Searching for FFmpeg...")

         # --- STEP 1: Check Global PATH (System Installation) ---
        system_ffmpeg = shutil.which("ffmpeg")
        if system_ffmpeg:
            print(f"[System] Global FFmpeg found at: {system_ffmpeg}")

        # --- STEP 2: Local Check & Setup ---
        print("[System] Global FFmpeg not found. Switching to Local mode...")

        system_os = platform.system()
        exe_name = "ffmpeg.exe" if system_os == "Windows" else "ffmpeg"

        # Determine base path
        if getattr(sys,'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        target_path = os.path.join(base_path, exe_name)

        # Check if we already have it locally
        if os.path.exists(target_path):
            print(f"[System] Local FFmpeg found at: {target_path}")
            return target_path
        
        try:
            print("[System] Local FFmpeg not found. Extracting from imageio library...")

            # Get the path of the binary inside the library
            source_path = imageio_ffmpeg.get_ffmpeg_exe()

            # Copy it to our project folder
            shutil.copy2(source_path, target_path)
            print(f"[System] Successfully copied to: {target_path}")

            # Grant execution permissions for Linux/macOS
            if system_os != "Windows":
                st = os.stat(target_path)
                os.chmod(target_path, st.st_mode | stat.S_IEXEC)
                print("[System] Execution permissions granted (chmod +x).")

            return target_path
        
        except Exception as e:
            messagebox.showerror("Critical Error", f"Failed to setup FFmpeg: {e}")
            return None
        
    def auto_update_ytdlp(self):
        """Updates yt-dlp via pip with timeout to prevent freezing."""
        if getattr(sys, 'frozen', False): return

        try:
            print("Checking for updates...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], 
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
            print("yt-dlp is up to date.")
        except Exception:
            print("Update check failed or timed out (Continuing...).")

    def create_widgets(self):
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        p = {'padx': 10, 'pady': 5}

        # URL Input
        tk.Label(self.root, text="Video URL:").grid(row=0, column=0, sticky="w", **p)
        self.url_entry = tk.Entry(self.root, textvariable=self.video_url)
        self.url_entry.grid(row=0, column=1, sticky="ew", **p)
        self.url_entry.bind("<FocusOut>", lambda e: self.start_fetch_qualities_thread())
        self.url_entry.bind("<Return>", lambda e: self.start_fetch_qualities_thread())

        # Filename Input
        tk.Label(self.root, text="Filename:").grid(row=1, column=0, sticky="w", **p)
        tk.Entry(self.root, textvariable=self.video_title).grid(row=1, column=1, sticky="ew", **p)

        # Folder Selection
        tk.Button(self.root, text="Select Folder", command=self.select_folder).grid(row=2, column=0, sticky="ew", **p)
        tk.Label(self.root, textvariable=self.download_path, fg="blue").grid(row=2, column=1, sticky="w", **p)

        # Format Selection
        tk.Label(self.root, text="Format:").grid(row=3, column=0, sticky="e", **p)
        cb = ttk.Combobox(self.root, textvariable=self.format_choice, values=["mp4", "mp3 (Audio Only)"], state="readonly")
        cb.grid(row=3, column=1, sticky="w", **p)
        cb.bind("<<ComboboxSelected>>", self.on_format_change)

        # Quality Selection
        self.lbl_qual = tk.Label(self.root, text="Quality:")
        self.lbl_qual.grid(row=4, column=0, sticky="e", **p)
        self.menu_qual = ttk.Combobox(self.root, textvariable=self.quality_choice, state="readonly")
        self.menu_qual.grid(row=4, column=1, sticky="ew", **p)

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, mode='determinate')
        self.progress.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=15)
        
        self.status_lbl = tk.Label(self.root, text="Ready", fg="grey")
        self.status_lbl.grid(row=6, column=0, columnspan=2)

        # Buttons
        self.btn_dl = tk.Button(self.root, text="DOWNLOAD", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.start_download)
        self.btn_dl.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        self.btn_cncl = tk.Button(self.root, text="Cancel", bg="#f44336", fg="white", font=("Arial", 10, "bold"), command=self.cancel_download, state="disabled")
        self.btn_cncl.grid(row=8, column=0, columnspan=2, sticky="ew", padx=10, pady=(0,10))  

    def select_folder(self):
        path = filedialog.askdirectory()
        if path: self.download_path.set(path)

    def on_format_change(self, e):
        if "mp3" in self.format_choice.get():
            self.lbl_qual.grid_remove()
            self.menu_qual.grid_remove()
        else:
            self.lbl_qual.grid()
            self.menu_qual.grid()
            self.start_fetch_qualities_thread()

    def start_fetch_qualities_thread(self):
        url = self.video_url.get().strip()
        if not url or "mp3" in self.format_choice.get():return
        self.status_lbl.config(text="Analyzing...", fg="orange")
        threading.Thread(target=self.fetch_qualities, daemon=True).start()

    def fetch_qualities(self):
        try:
            # Added 'force_ipv4' to fix timeouts on some networks
            opts = {'quiet': True, 'force_ipv4': True, 'socket_timeout': 10}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(self.video_url.get(), download=False)
                self.video_title.set(info.get('title', 'Video'))
                formats = info.get('formats', [])
                valid = []
                for f in formats:
                    if f.get('ext') == 'mp4' and f.get('vcodec') != 'none':
                        h = f.get('height')
                        if h:
                            sz = f.get('filesize_approx', 0) or f.get('filesize', 0)
                            mb = f"{sz/1e6:.1f} MB" if sz else ""
                            valid.append((h, f"{h}p {mb} | ID: {f['format_id']}"))
                
                valid.sort(key=lambda x: x[0], reverse=True)
                final = [x[1] for x in valid]
                
                def update():
                    self.menu_qual['values'] = list(dict.fromkeys(final))
                    if final: self.menu_qual.current(0)
                    self.status_lbl.config(text="Qualities loaded.", fg="green")
                self.root.after(0, update)
        except Exception as e:
            print(e)
            self.root.after(0, lambda: self.status_lbl.config(text="Fetch Failed (Check URL/Net)", fg="red"))

    def start_download(self):
        if not self.ffmpeg_path:
            messagebox.showerror("Error", "FFmpeg missing or setup failed.")
            return
        if not self.video_url.get() or not self.download_path.get():
            messagebox.showwarning("Missing Info", "Please select URL and Folder.")
            return

        self.downloading = True
        self.cancelled = False
        self.btn_dl.config(state="disabled")
        self.btn_cncl.config(state="normal")
        self.progress['value'] = 0
        threading.Thread(target=self.run_download, daemon=True).start()

    def run_download(self):
        url = self.video_url.get()
        path = self.download_path.get()
        
        print(f"[Download] Using FFmpeg at: {self.ffmpeg_path}")

        # --- KEY CONFIGURATION ---
        opts = {
            'outtmpl': os.path.join(path, f'{self.video_title.get()}.%(ext)s'),
            'ffmpeg_location': self.ffmpeg_path, 
            'progress_hooks': [self.hook],
            'quiet': True,
            'nocheckcertificate': True,
            'force_ipv4': True, 
            'socket_timeout': 15,
        }

        if "mp3" in self.format_choice.get():
            opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]})
        else:
            sel = self.quality_choice.get()
            fid = sel.split("ID: ")[1] if "ID: " in sel else "bestvideo+bestaudio/best"
            opts['format'] = f"{fid}+bestaudio/best" if "ID: " in sel else "bestvideo+bestaudio/best"

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                self.ydl = ydl
                ydl.download([url])
            if not self.cancelled:
                self.root.after(0, lambda: messagebox.showinfo("Success", "Download Complete!"))
                self.root.after(0, lambda: self.status_lbl.config(text="Done.", fg="green"))
        except Exception as e:
            if not self.cancelled:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, self.reset_ui)

    def hook(self, d):
        if self.cancelled: raise Exception("Cancelled")
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 1)
            p = (d.get('total_bytes', 0) / total) * 100
            self.root.after(0, lambda: self.progress.configure(value=p))
            self.root.after(0, lambda: self.status_lbl.config(text=f"{p:.1f}%"))

    def cancel_download(self):
        self.cancelled = True
        self.status_lbl.config(text="Stopping...", fg="red")

    def reset_ui(self):
        self.downloading = False
        self.btn_dl.config(state="normal")
        self.btn_cncl.config(state="disabled")
        self.progress['value'] = 0
        if not self.cancelled: self.status_lbl.config(text="Ready")

if __name__ == "__main__":
    root = tk.Tk()
    app = MyTubeDownloader(root)
    root.mainloop()