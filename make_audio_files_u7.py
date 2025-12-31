# make_audio_files.py
from gtts import gTTS

words = [
    "開開心心",
    "大街上",
    "滿街",
    "雙眼",
    "看哪看",
    "左思右想",
    "胖國王",
    "衣裳",
    "一針一線",
    "簡單",
    "聰明",
    "大臣",
    "不敢",
    "東西",
    "慌張",
    "一直",
    "好棒"
]

for w in words:
    tts = gTTS(w, lang="zh-tw")
    filename = f"audio_u7/{w}.mp3"
    tts.save(filename)
    print("已產生：", filename)
