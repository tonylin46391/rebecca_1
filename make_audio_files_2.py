# -*- coding: utf-8 -*-
"""
make_audio_files.py
根據 003_ELA_P26.py 的 word_bank：
為每一筆產生 3 種 mp3：
1) 單字英文發音
2) 英文例句（已把 ??? 替換為單字）
3) 中文翻譯句子
"""

import os
from gtts import gTTS, gTTSError

word_bank = [
    {"word": "agency", "translation": "代辦處；經銷處；政府機構",
     "sentence": "Many people worked at the agency.",
     "sentence_zh": "許多人在這家代辦處工作。"},
    
    {"word": "business", "translation": "生意；業務；商店",
     "sentence": "My aunt opened a small business that sells coffee.",
     "sentence_zh": "我阿姨開了一家賣咖啡的小店。"},
     
    {"word": "confidently", "translation": "自信地；有信心地",
     "sentence": "Tia confidently stood up to give her report.",
     "sentence_zh": "Tia 自信地站起來做報告。"},
     
    {"word": "eagerly", "translation": "熱切地；渴望地",
     "sentence": "The family eagerly explored their new home.",
     "sentence_zh": "這家人熱切地探索他們的新家。"},
     
    {"word": "seeps", "translation": "滲出；緩慢穿過",
     "sentence": "The sand seeps through the hourglass.",
     "sentence_zh": "沙子緩慢地從沙漏中滲出。"},
     
    {"word": "mystery", "translation": "謎；難以理解的事物",
     "sentence": "The contents of the box are a mystery.",
     "sentence_zh": "箱子裡的內容物是個謎。"},
     
    {"word": "ace", "translation": "高手；一流人才",
     "sentence": "He is an ace athlete.",
     "sentence_zh": "他是一位一流的運動員。"},
     
    {"word": "located", "translation": "位於；坐落於",
     "sentence": "The alligator pond was located near the center of the zoo.",
     "sentence_zh": "鱷魚池位於動物園的中心附近。"},
]

AUDIO_DIR = "audio"  # mp3 會存放在 ./audio 資料夾


def main():
    print("=== make_audio_files.py 開始執行 ===")
    print("將為題庫中的單字產生：單字 / 英文例句 / 中文例句 的 mp3 檔案...\n")

    # 確保 audio 資料夾存在
    os.makedirs(AUDIO_DIR, exist_ok=True)
    print(f"已確認/建立資料夾: {AUDIO_DIR}")
    print("-" * 40)

    for idx, item in enumerate(word_bank, start=1):
        word = item["word"]
        sentence_tpl = item["sentence"]
        sentence_zh = item["sentence_zh"]

        # 把英文句子中的 ??? 替換為單字
        sentence_en = sentence_tpl.replace("???", word)

        # 檔名前加上編號，方便辨識順序與避免重複 close 被覆蓋
        base = f"{idx:02d}_{word}"

        paths = {
            "word_en": os.path.join(AUDIO_DIR, f"{base}_word_en.mp3"),
            "sent_en": os.path.join(AUDIO_DIR, f"{base}_sent_en.mp3"),
            "sent_zh": os.path.join(AUDIO_DIR, f"{base}_sent_zh.mp3"),
        }

        print(f"[{idx:02d}] 單字: {word}")
        print(f"    英文句子: {sentence_en}")
        print(f"    中文句子: {sentence_zh}")

        # 1) 單字英文發音
        try:
            print(f"    ▶ 產生單字音檔: {paths['word_en']} ...", end="", flush=True)
            tts_word = gTTS(text=word, lang="en")
            tts_word.save(paths["word_en"])
            print(" OK")
        except gTTSError as e:
            print(" 失敗（gTTSError）：", e)
        except Exception as e:
            print(" 失敗（其他錯誤）：", e)

        # 2) 英文例句發音
        try:
            print(f"    ▶ 產生英文例句音檔: {paths['sent_en']} ...", end="", flush=True)
            tts_sent_en = gTTS(text=sentence_en, lang="en")
            tts_sent_en.save(paths["sent_en"])
            print(" OK")
        except gTTSError as e:
            print(" 失敗（gTTSError）：", e)
        except Exception as e:
            print(" 失敗（其他錯誤）：", e)

        # 3) 中文例句發音
        try:
            print(f"    ▶ 產生中文句子音檔: {paths['sent_zh']} ...", end="", flush=True)
            tts_sent_zh = gTTS(text=sentence_zh, lang="zh-TW")
            tts_sent_zh.save(paths["sent_zh"])
            print(" OK")
        except gTTSError as e:
            print(" 失敗（gTTSError）：", e)
        except Exception as e:
            print(" 失敗（其他錯誤）：", e)

        print("-" * 40)

    print("✅ 全部處理完畢，請打開 audio 資料夾查看 mp3 檔案。")
    input("按 Enter 結束程式...")


if __name__ == "__main__":
    main()
