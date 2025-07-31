import os
import threading
import shutil
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import yt_dlp

class YouTubeToMP3App:
    def __init__(self, master):
        self.master = master
        master.title("YouTube to MP3 Converter")

        self.url_label = tk.Label(master, text="YouTube URL:")
        self.url_label.pack(pady=(10, 0))

        self.url_entry = tk.Entry(master, width=50)
        self.url_entry.pack(pady=5)

        self.convert_button = tk.Button(master, text="Convert", command=self.start_conversion_thread)
        self.convert_button.pack(pady=5)

        self.download_button = tk.Button(master, text="Download", state=tk.DISABLED, command=self.choose_download_location)
        self.download_button.pack(pady=5)

        self.progress_label = tk.Label(master, text="Idle")
        self.progress_label.pack(pady=5)

        self.progress_bar = ttk.Progressbar(master, orient='horizontal', length=300, mode='determinate')
        self.progress_bar.pack(pady=5)

        self.converting_bar = ttk.Progressbar(master, orient='horizontal', length=300, mode='indeterminate')
        self.converting_bar.pack(pady=(5, 10))

        self.audio_file = None

    def start_conversion_thread(self):
        thread = threading.Thread(target=self.convert_video)
        thread.start()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0.0%').strip().replace('%', '')
            try:
                self.progress_bar['value'] = float(percent)
                self.progress_label.config(text=f"Downloading... {percent}%")
            except ValueError:
                pass
        elif d['status'] == 'finished':
            self.progress_bar['value'] = 100
            self.progress_label.config(text="Download complete. Converting...")
            self.converting_bar.start(10)

    def convert_video(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return

        self.download_button.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Starting download...")

        def do_conversion():
            try:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': 'temp_audio.%(ext)s',
                    'noplaylist': True,
                    'quiet': True,
                    'progress_hooks': [self.progress_hook],
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                # Locate converted file
                for file in os.listdir():
                    if file.startswith("temp_audio") and file.endswith(".mp3"):
                        self.audio_file = file
                        break

                if self.audio_file:
                    self.progress_label.config(text="Conversion finished. Ready to save.")
                    self.converting_bar.stop()
                    self.download_button.config(state=tk.NORMAL)
                else:
                    self.progress_label.config(text="Conversion failed.")
                    messagebox.showerror("Error", "Converted file not found.")

            except Exception as e:
                self.converting_bar.stop()
                self.progress_label.config(text="Error during conversion.")
                messagebox.showerror("Conversion Failed", str(e))

        threading.Thread(target=do_conversion).start()

    def choose_download_location(self):
        if not self.audio_file or not os.path.exists(self.audio_file):
            messagebox.showerror("Error", "No converted file found.")
            return

        dest_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3")],
            title="Save As"
        )

        if dest_path:
            try:
                shutil.move(self.audio_file, dest_path)
                self.progress_label.config(text="File saved successfully.")
                self.download_button.config(state=tk.DISABLED)
                messagebox.showinfo("Success", f"Saved to: {dest_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to move file:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeToMP3App(root)
    root.mainloop()
