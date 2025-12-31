# make_audio_files.py
from gtts import gTTS


# 題庫
words = [ 
    "答對了",  "答錯了", "加油"
] 




for w in words:
    tts = gTTS(w, lang="zh-tw")
    filename = f"audio/{w}.mp3"
    tts.save(filename)
    print("已產生：", filename)
