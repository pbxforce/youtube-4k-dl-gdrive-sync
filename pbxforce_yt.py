import os
from moviepy.editor import *
from pytube import YouTube
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import re
import yaml
import subprocess
import urllib.parse
import requests
from time import sleep
from pathlib import Path
import argparse


# Function to remove non-alphabet characters from the title.
def remove_non_alpha(s):
    return re.sub(r'[^a-zA-Z\s]', '', s).replace(' ', '-')


# Declaring optional arguments that can be passed executing script
parser = argparse.ArgumentParser()
parser.add_argument('--keep-local', action='store_true',
                    help='Do not delete locally downloaded files after script completion')
parser.add_argument('--no-drive', action='store_true',
                    help='Do not interact with google drive. Should be used to save videos in local system only')
args = parser.parse_args()

CWD = Path.cwd()
output_dir = CWD / 'yt-downloader'
if output_dir.is_dir():
    pass
else:
    output_dir.mkdir(parents=True, exist_ok=True)

# Managing settings.yaml file
if not args.no_drive:
    try:
        # Absolute path of settings.yaml file. This file should be in the same directory where the script file is.
        settings_path = CWD / 'settings.yaml'

        # Checking if credentials.json file is present so that we won't overwrite the client id and secret key in settings.yaml.
        if (CWD / 'credentials.json').is_file():
            gauth = GoogleAuth(settings_file=settings_path)
            gauth.LocalWebserverAuth()
            drive = GoogleDrive(gauth)
            print("Google-drive credentials loaded.")
        else:
            with open(settings_path, 'r') as f:
                settings = yaml.safe_load(f)

            # Prompt the user to enter their client id and secret
            print('Setting up google drive credentials. Make sure you enter client id and client secret correctly..')
            clientId = input('Enter your client id: ')
            clientSecret = input('Enter your client secret: ')

            # Update the fields in the dictionary with the user's input
            settings['client_config']['client_id'] = clientId
            settings['client_config']['client_secret'] = clientSecret

            # Write the updated dictionary back to the settings.yaml file
            with open(settings_path, 'w') as f:
                yaml.safe_dump(settings, f, sort_keys=False)

            # Google drive setup
            gauth = GoogleAuth(settings_file=settings_path)
            gauth.LocalWebserverAuth()
            drive = GoogleDrive(gauth)
            print("Google-drive credentials loaded.")
    except ValueError as e:
        print("Error:", e)
        exit()

# Validating input url
try:
    video_url = input("Paste YouTube URL: ")
    result = urllib.parse.urlparse(video_url)

    # Check if the URL is valid and belongs to youtube.com
    if result.scheme == "https" and result.netloc == "www.youtube.com":
        print("URL check... PASS")
        try:
            yt = YouTube(video_url)
        except:
            print("Failed to read url. Retrying...")
            sleep(2)
            yt = YouTube(video_url)
        raw_title = yt.title
        title = remove_non_alpha(raw_title)

        # Send a request to the URL and check if the video is available
        response = requests.get(video_url)
        if "Video unavailable" in response.text:
            print("Video is not available on YouTube")
            raise ValueError("Video is not available on YouTube")
        else:
            print(f"Title: {title}")
            print("Gathering available streams...")
            sleep(2)

    else:
        print("URL is not valid or does not belong to youtube.com")
        raise ValueError("Invalid URL or URL does not belong to youtube.com")

    # Audio bitrate for 'audio_only' and merging video/audio above 1080p. Bitrate 160kbps can also be used for 2K and 4K videos.
    audio_bitrate = '128kbps'

    # Getting list of all available streams except 144p for input url.
    streams = list(yt.streams.filter(progressive=True).order_by('resolution').desc())
    hd_1 = yt.streams.filter(res='1080p').first()
    hd_2 = yt.streams.filter(res='1440p').first()
    hd_3 = yt.streams.filter(res='2160p').first()
    resolutions = set(stream.resolution for stream in streams + [hd_1, hd_2, hd_3] if
                      stream and stream.resolution and stream.resolution != '144p')
    resolutions_list = sorted(resolutions, key=lambda x: int(x[:-1]))
    resolutions_list.append('audio')
    download_quality = input(f"Enter download quality: Available streams are {resolutions_list}: ")
    file_name = f"protocolten-{title}"
    output_path = os.path.join(output_dir, file_name)

    # This condition only handle downloading and uploading of audio-only file
    if download_quality == 'audio':
        audio_only = yt.streams.filter(abr=audio_bitrate).first()
        print("Downloading audio-only file...")
        audio_only.download(output_path=output_dir, filename=f"{file_name}.m4a")

        if not args.no_drive:
            # Uploading file to google drive
            output_file_drive = drive.CreateFile({'title': f"{file_name}.m4a"})
            output_file_drive.SetContentFile(f"{output_path}.m4a")
            print("Uploading file to drive...")
            output_file_drive.Upload()

            # Permissions for uploading file. Anyone with link can access it.
            output_file_drive.InsertPermission({
                'type': 'anyone',
                'value': 'anyone',
                'role': 'reader'
            })

        # Deleting locally saved file if --keep-local is not passed while executing script
        if not args.keep_local:
            print("Deleting locally saved file...")
            os.remove(f'{output_path}.m4a')

        # Getting direct download link of uploaded file from google drive
        if not args.no_drive:
            download_link = output_file_drive['webContentLink']
            print(f"File uploaded to Google Drive. Direct download link for {download_quality} is: {download_link}")
            exit()
        else:
            print(f"File has been saved in: {output_dir}")
            exit()

    # This condition only handle downloading and uploading of 360p/720p videos
    elif download_quality in ['360p', '720p']:
        stream = yt.streams.filter(res=download_quality).first()
        print("Downloading video stream...")
        video_file = stream.download(output_path=output_dir, filename=f"{file_name}.mp4")

        # Uploading file to google drive
        if not args.no_drive:
            output_file_drive = drive.CreateFile({'title': f"{file_name}.mp4"})
            output_file_drive.SetContentFile(f"{output_path}.mp4")
            print("Uploading file to drive...")
            output_file_drive.Upload()

            # Permissions for uploading file. Anyone with link can access it.
            output_file_drive.InsertPermission({
                'type': 'anyone',
                'value': 'anyone',
                'role': 'reader'
            })

        # Deleting locally saved file if --keep-local is not passed while executing script
        if not args.keep_local:
            print("Deleting locally saved file...")
            os.remove(f'{output_path}.mp4')

        # Getting direct download link of uploaded file from google drive
        if not args.no_drive:
            download_link = output_file_drive['webContentLink']
            print(f"File uploaded to Google Drive. Direct download link for {download_quality} is: {download_link}")
            exit()
        else:
            print(f"File has been saved in: {output_dir}")
            exit()

    # Getting input stream and downloading it into specific directory
    elif download_quality in ['1080p', '1440', '2160p']:
        stream = yt.streams.filter(res=download_quality).first()
        audio_stream = yt.streams.filter(abr=audio_bitrate).first()

        # Checking if audio and video streams are present for input link
        if not stream:
            raise ValueError(f"No video stream found for {download_quality}")
        if not audio_stream:
            raise ValueError(f"No audio stream found for {download_quality}")

        # Downloading audio and video files
        print("Downloading video stream...")
        video_file = stream.download(output_path=output_dir, filename="video.mp4")
        print("Downloading audio stream...")
        audio_file = audio_stream.download(output_path=output_dir, filename="audio.mp4")

        # Combining the audio and video file using ffmpeg tool.
        print("Merging video and audio files...")
        command = f"echo 'y' | ffmpeg -i {video_file} -i {audio_file} -c:v copy -c:a copy {output_path}.mp4"
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if not args.no_drive:
            # Uploading file to google drive
            output_file_drive = drive.CreateFile({'title': f"{file_name}.mp4"})
            output_file_drive.SetContentFile(f"{output_path}.mp4")
            print("Uploading file to drive...")
            output_file_drive.Upload()

            # Permissions for uploading file. Anyone with link can access it.
            output_file_drive.InsertPermission({
                'type': 'anyone',
                'value': 'anyone',
                'role': 'reader'
            })

        # Deleting locally saved files if --keep-local is not passed while executing script
        if not args.keep_local:
            print("Deleting locally saved files...")
            if 'video_file' in locals() and os.path.exists(video_file):
                os.remove(video_file)
            if 'audio_file' in locals() and os.path.exists(audio_file):
                os.remove(audio_file)
            if os.path.exists(f'{output_path}.mp4'):
                os.remove(f'{output_path}.mp4')

        # Getting direct download link of uploaded file from google drive
        if not args.no_drive:
            download_link = output_file_drive['webContentLink']
            print(f"File uploaded to Google Drive. Direct download link for {download_quality} is: {download_link}")
            exit()
        else:
            print(f"File has been saved in: {output_dir}")
        exit()

except Exception as e:
    print(f"Error: {e}")
