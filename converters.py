import subprocess
from PIL import Image
import yt_dlp
import os

SOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"
# если 32-bit:
# SOFFICE_PATH = r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"

def image_to_pdf(image_path, output_path):
    img = Image.open(image_path).convert("RGB")
    img.save(output_path)

def png_to_jpg(png_path, jpg_path):
    img = Image.open(png_path).convert("RGB")
    img.save(jpg_path)

def video_to_gif(video_path, output_path):
    subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-vf", "scale=480:-1", output_path],
        check=True
    )

def video_to_mp3(video_path, output_path):
    subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, output_path],
        check=True
    )

def docx_to_pdf(docx_path, output_dir):
    subprocess.run(
        [
            SOFFICE_PATH,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            docx_path
        ],
        check=True
    )

# ---------- СКАЧИВАНИЕ ПО ССЫЛКЕ ----------
def download_by_url(url: str, output_path: str):
    ydl_opts = {
        "outtmpl": output_path,
        "format": "mp4",
        "quiet": True,
        "noplaylist": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
