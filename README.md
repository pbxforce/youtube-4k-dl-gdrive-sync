# youtube-4k-dl-gdrive-sync
### About
#### This script only work on linux

This python script is based of Pytube2 and Pydrive. A simple python script that you can use Automate the process of YouTube video downloading. Due to YouTube using DASH, videos downloaded above 720p using Pytube2 does not have any audio. Using this script, now It's possible to download video upto 4K without any audio problem. Just Paste the link, choose the quality and you are good to go.

Pydrive is used to interact with Google Drive via API. You must have OAuth Client ID and Client Secret to upload downloaded YouTube video into your Google Drive. You can get that from: https://console.cloud.google.com/apis/credentials

Tested and written on Python 3.10.6

Install requirements:

    pip install -r requirements.txt

Run the script and follow the instructions:

    python pbxforce_yt.py

On first initilization, you'll have to setup google drive credentials. Paste your Client ID and Client Secret. A browser window will open for google drive authentication. After successfull login, a file by the name of credentials.json will be generated in your project directory. From now on, instead of login again and again, this credentials file will be used to interact with google drive.

### Working of script

Working is pretty straightforward. Just paste the YouTube video link and You will be presented with the list of all available quality options for that particular video. You'll also have the option to <b>download only audio.</b> 

Downloaded files are saved in the system under <b>protocolten/</b> directory, which will be created inside the project directory.

By default, this script will set up google drive credentials, then input for youtube link, download and upload the video to your google drive, and provide you a direct download. After uploading the file to google drive, files saved in the system will be deleted automatically.

<b>To keep the downloaded video files in the system after uploading to Google Drive, you can run the script with this optional argument:</b>

    python pbxforce_yt.py --keep-local
    
With this optional argument, video files will be saved in the system as well as uploaded to google drive. These files will be saved inside the project directory under <b>protocolten/</b> directory.

<b>If you don't want to interact with Google Drive or don't want to upload files to google drive, then you can pass this optional argument along with --keep-local argument:</b>

    python pbxforce_yt.py --keep-local --no-drive
    
With these optional arguments, your video file will be locally downloaded into the system and it won't be uploaded to your google drive. In other words, if you just want to download and save videos in your system and don't want to interact with google drive, you should pass both arguments to the script.

There is no limit on file size while uploading to google drive using API. But you might wanna check with the Google official documentation for API limits and file sizes. As far as I know, google allows file up to 5TB to be uploaded using API. However neither this script nor pydrive limits the file size, so there should not be any issue regarding file size. This script is tested up to 5GB.
