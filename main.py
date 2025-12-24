import asyncio
from shazamio import Shazam
from shazamio.exceptions import FailedDecodeJson
import time
import os
import asyncio
from datetime import datetime
import subprocess
from pathlib import Path

VIDEO_EXT = ".mp4"
AUDIO_EXT = ".wav"
MAX_RETRIES = 100
RETRY_DELAY = 60  # seconds (5 minutes)
VIDEO_EXTENSIONS = (".mp4", ".mkv", ".avi", ".mov", ".flv", ".webm")


class RateLimitError(Exception):
    pass

async def identify_song(audio_path):
    shazam = Shazam()
    
    try:
        result = await shazam.recognize_song(audio_path)
        print(result["track"]["title"], "-", result["track"]["subtitle"])
        return result["track"]["title"]
    
    except FailedDecodeJson:
        print("⚠️ Shazam rate-limited")
        raise RateLimitError("Shazam rate limited")
    except Exception as e:
        print(f"⚠️ Shazam error: {e}")
        return None

def safe_filename(name):
    return "".join(c for c in name if c.isalnum() or c in " _-").rstrip()


async def process_folder(folder_path):
    
    for file in os.listdir(folder_path):
        if not file.lower().endswith(VIDEO_EXT):
            continue

        mp4_path = os.path.join(folder_path, file)
        base_name = os.path.splitext(file)[0]
        wmv_path = os.path.join(folder_path, base_name + AUDIO_EXT)

        if not os.path.exists(wmv_path):
            pass
        else:
            print(f"\n▶ Processing: {file}")

            # 2️⃣ Identify song
            song_name = await identify_song(wmv_path)
            await asyncio.sleep(21)  # prevent 429
            if song_name:
                song_name = safe_filename(song_name)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_mp4 = os.path.join(
                    folder_path,
                    f"{song_name}_{timestamp}{VIDEO_EXT}"
                )
                os.rename(mp4_path, new_mp4)
                print(f"✅ Renamed to: {os.path.basename(new_mp4)}")

            else:
                print("❌ Song not identified — MP4 unchanged")
            
            # 3️⃣ ALWAYS delete WMV   
            if os.path.exists(wmv_path):
                os.remove(wmv_path)
                print("🧹 Temp WMV deleted")
        
            
class ProcessInterrupted(Exception):
    def __init__(self, cum_video):
        self.cum_video = cum_video


async def main(input_dir):
    
    attempt = 0
    output_dir = input_dir
    output_dir.mkdir(exist_ok=True)
    num_video = 0

    for video_path in input_dir.iterdir():
        if video_path.suffix.lower() in VIDEO_EXTENSIONS:
            output_audio = output_dir / f"{video_path.stem}.wav"
            cmd = [
                "ffmpeg",
                "-y",                  # overwrite
                "-i", str(video_path),
                "-vn",                 # no video
                "-acodec", "pcm_s16le",
                "-ar", "44100",
                "-ac", "1",             # mono (change to 2 if needed)
                str(output_audio)
            ]
            print(f"Extracting: {video_path.name}")
            num_video += 1
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    while attempt < MAX_RETRIES:

        try:
            print("----- Total number of videos: ",num_video, " Videos ------")
            await process_folder(input_dir)
            break

        except Exception as e:
            attempt += 1
            print(f"⚠️ Error occurred: {e}")
            print(f"🔁 Retry {attempt}/{MAX_RETRIES} in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)

        print("❌ Max retries reached. Exiting.")


if __name__ == "__main__":
    asyncio.run(main(Path(r"FOLDER_NAME_HERE")))    # folder with videos))
