# make_audio_files.py
from gtts import gTTS

words = [
    "小鎮", "柿餅", "節日", "新埔", "因此",
    "走進", "彩排", "遠方", "金黃色", "可愛",
    "月亮", "風乾", "香甜", "遊客", "買書",
    "親朋好友", "如意", "進去", "最近", "學校"
]

for w in words:
    tts = gTTS(w, lang="zh-tw")
    filename = f"audio/{w}.mp3"
    tts.save(filename)
    print("已產生：", filename)
