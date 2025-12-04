📺 MyTube Downloader

MyTube Downloader is a robust, high-performance desktop application built with Python and Tkinter. It provides a user-friendly GUI for downloading videos and audio from YouTube in the highest available quality.

🚀 Key Differentiator: This application features Smart FFmpeg Management. It automatically handles the complex FFmpeg dependency, ensuring the app works on any computer immediately—even if the user hasn't installed FFmpeg manually.

🌟 Key Features

✅ Auto-FFmpeg Setup: Detects if FFmpeg is missing and automatically extracts/installs it for the user. No manual configuration required.

✅ Non-Blocking UI (Threading): Downloads and updates run in background threads, keeping the interface responsive and freeze-free.

✅ Format Selection: Choose between Video (MP4) or Audio Only (MP3).

✅ Smart Quality Detection: Automatically fetches available resolutions (1080p, 720p, etc.) and file sizes before downloading.

✅ Auto-Updates: Automatically checks and updates the yt-dlp core engine on launch to ensure compatibility with YouTube changes.

✅ Real-time Progress: Visual progress bar showing download percentage and status.

🚀 How to Use (For Users)

No coding knowledge required. You can simply download the executable file.

Go to the [download](./) page of this repository.

Download the latest project file .

Run the application (Just needed latest version of the Python).

Paste a YouTube link, select a folder, and hit DOWNLOAD.

🛠️ Installation (For Developers)

If you want to run the source code or contribute, follow these steps:

Prerequisites

Python 3.8 or higher

1. Clone the Repository

git clone [https://github.com/manji5/MyTubeDownloader.git](https://github.com/manji5/MyTubeDownloader.git)
cd MyTubeDownloader

2. Create a Virtual Environment (Recommended)

# Windows

python -m venv venv
.\venv\Scripts\activate

# macOS/Linux

python3 -m venv venv
source venv/bin/activate

3. Install Dependencies

pip install yt-dlp imageio-ffmpeg

(Tkinter is included with standard Python installations)

4. Run the App

python main.py

🧩 Technical Architecture

This project solves the common "FFmpeg missing" error using a hybrid approach:

System Check: First, it checks the system PATH for a global ffmpeg installation.

Local Check: If not found, it checks for ffmpeg.exe in the application's root directory.

Auto-Extraction: If both fail, it utilizes the imageio_ffmpeg library to extract a binary copy of FFmpeg and places it in the working directory, granting necessary execution permissions (chmod +x) on Linux/macOS.

Building the Executable (.exe)

To build a standalone .exe file using PyInstaller:

pip install pyinstaller
pyinstaller --noconsole --onefile --name="MyTubeDownloader" main.py

📄 License

This project is licensed under the MIT License

Developed by: [Fatih Enes/manji5]
