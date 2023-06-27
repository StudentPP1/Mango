# Mango
Universal music Telegram bot

# Installation
Clone the repository:
```
git clone https://github.com/StudentPP1/Mango.git
```

Install the required packages:
```
pip install -r requirements.txt
```

run:
```
python main.py
```

# Start
To start using the bot:
+ create an environment variable with a token for the bot (Get the token from [@BotFather](https://t.me/BotFather))

+ download [ffmpeg](https://ffmpeg.org/) and add the absolute path to 'ffmpeg.exe' to the ``functions/loader.py``
```
ydl_opts = {'format': 'bestvideo+bestaudio/best',
            "ffmpeg_location": r "your absolute path to 'ffmpeg.exe'"}
```

+ create a group chat with the bot

# Features
Bot capabilities:
+ download music from YouTube ( single tracks or open playlists)
+ delete music 
+ create playlists
+ delete playlists
+ You can send music files to a group with the bot and they will be automatically added to your tracks




