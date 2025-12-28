import subprocess
from PIL import Image

def image_to_pdf(image_path, output_path):
    img = Image.open(image_path).convert("RGB")
    img.save(output_path)

def video_to_gif(video_path, output_path):
    subprocess.run([
        "ffmpeg", "-i", video_path,
        "-vf", "scale=480:-1",
        output_path
    ])
