import os
import subprocess
import yt_dlp
import requests
from bs4 import BeautifulSoup
from PIL import Image

SOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"


# ---------- КОНВЕРТАЦИИ ----------
def image_to_pdf(image_path, output_path):
    Image.open(image_path).convert("RGB").save(output_path)


def png_to_jpg(png_path, jpg_path):
    Image.open(png_path).convert("RGB").save(jpg_path)


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


# ---------- PINTEREST HTML ----------
def parse_pinterest(url: str):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    video = soup.find("meta", property="og:video")
    image = soup.find("meta", property="og:image")

    return {
        "video": video["content"] if video else None,
        "image": image["content"] if image else None,
    }


# ---------- СКАЧИВАНИЕ ПО ССЫЛКЕ ----------
def download_by_url(url: str, output_dir: str) -> dict:
    """
    return:
    {
        "type": "video" | "photo",
        "files": [paths]
    }
    """
    os.makedirs(output_dir, exist_ok=True)

    # 🟢 yt-dlp (видео)
    try:
        files = []

        ydl_opts = {
            "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
            "quiet": True,
            "noplaylist": True,
            "merge_output_format": "mp4",
        }

        def hook(d):
            if d["status"] == "finished":
                files.append(d["filename"])

        ydl_opts["progress_hooks"] = [hook]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if files:
            return {"type": "video", "files": files}

    except Exception as e:
        yt_error = str(e)

    # 🟡 Pinterest fallback
    if "pinterest" in url:
        data = parse_pinterest(url)

        if data["video"]:
            path = os.path.join(output_dir, "pinterest_video.mp4")
            r = requests.get(data["video"], timeout=15)
            with open(path, "wb") as f:
                f.write(r.content)
            return {"type": "video", "files": [path]}

        if data["image"]:
            ext = data["image"].split(".")[-1].split("?")[0]
            path = os.path.join(output_dir, f"pinterest_image.{ext}")
            r = requests.get(data["image"], timeout=15)
            with open(path, "wb") as f:
                f.write(r.content)
            return {"type": "photo", "files": [path]}

        raise Exception("Pinterest media not accessible")

    # 🔴 Явные ограничения
    if "youtube" in url:
        raise Exception("YouTube ограничил загрузку")

    if "tiktok" in url:
        raise Exception("TikTok заблокировал IP")

    raise Exception("Unsupported URL")
