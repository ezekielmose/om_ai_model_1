import yt_dlp
import os
import uuid

# 🔥 NEW DOWNLOAD LOCATION
DOWNLOAD_DIR = r"D:\reels"


def download_reel(url):
    """
    Downloads each reel as a unique file into D:\reels
    """

    # Ensure folder exists
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    # Unique filename per reel
    unique_id = uuid.uuid4().hex
    output_path = os.path.join(DOWNLOAD_DIR, f"video_{unique_id}.mp4")

    ydl_opts = {
        "outtmpl": output_path,
        "format": "mp4/best",
        "quiet": True,
        "noplaylist": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except Exception as e:
        raise Exception(f"Download failed for {url}: {str(e)}")

    print(f"✔ Downloaded reel:")
    print(f"   URL : {url}")
    print(f"   PATH: {output_path}")

    return output_path
