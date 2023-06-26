import os
import subprocess
import yt_dlp
import eyed3
import requests
import re
from pytube import Playlist

ydl_opts = {"format": 'bestvideo+bestaudio/best',
            "ffmpeg_location": r"C:\ffmpeg\ffmpeg-2023-05-11-git-ceb050427c-full_build\bin\ffmpeg.exe"}


def download_video(url):
    if "&" in url[0]:
        video_id = url[0][url[0].index("=") + 1:url[0].index("&")]
    else:
        video_id = url[0][url[0].index("=") + 1:]

    with open("img.jpg", 'wb') as f:
        img = requests.get(f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg').content
        f.write(img)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)


def load_metadata_to_mp3(file_mp3, title):
    audio_file = eyed3.load(file_mp3)
    audio_file.tag.title = title
    audio_file.tag.images.set(3, open("img.jpg", 'rb').read(), 'image/jpeg')
    audio_file.tag.save()
    os.rename(f"{file_mp3}", f'{title}.mp3')
    return f"{title}.mp3"


def convert_video_to_audio_ffmpeg(video_file, output_ext="mp3"):
    filename, ext = os.path.splitext(video_file)
    subprocess.call([ydl_opts["ffmpeg_location"], "-y", "-i", video_file,
                     f"{filename}.{output_ext}"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def del_files():
    for f in os.listdir():
        if f.endswith('.jpg') or f.endswith('.mp4') or f.endswith('.webm'):
            os.remove(f)


def download_mp3_from_video(url):
    print("Downloading video...")

    download_video([url])
    ready_to_convert = False
    download_file = None

    while not ready_to_convert:
        for file in os.listdir():
            if file.endswith(".webm") or file.endswith(".mp4"):
                ready_to_convert = True
                download_file = file

    print("Converting video to audio...")
    convert_video_to_audio_ffmpeg(download_file, output_ext="mp3")

    print("Loading metadata to audio...")
    file_name = download_file.replace(".webm", ".mp3").replace(".mp4", ".mp3")
    title = re.sub(r'\[.+\]', '', file_name.replace(".mp3", "")).strip()

    audio = load_metadata_to_mp3(file_name, title)

    print("Deleting other files...")
    del_files()

    print(f"Done: {audio}")
    return audio


def download(url):
    try:
        audios = []
        if url.startswith('https://www.youtube.com/watch?'):
            audios.append(download_mp3_from_video(url))
            return audios

        elif url.startswith('https://www.youtube.com/playlist?'):
            print("Getting playlist...")
            videos = Playlist(url)
            video_urls = [video_url for video_url in videos.video_urls]
            for video_url in video_urls:
                audios.append(download_mp3_from_video(video_url))
                print(f"Done: {video_urls.index(video_url) + 1}/{len(video_urls)}")
            return audios

        else:
            raise SyntaxError
    except Exception as ex:
        print(f"Sorry, loader crashed: {ex}")
        raise SyntaxError
