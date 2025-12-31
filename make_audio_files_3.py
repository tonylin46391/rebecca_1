# -*- coding: utf-8 -*-
"""
make_audio_files.py
根據 word_bank：
為每一筆產生 5 種 mp3：
1) 單字英文發音 (word_en)
2) 英文例句發音 (sent_en)
3) 中文翻譯句子發音 (sent_zh)
4) 英文定義發音 (def_en) 
5) 中文定義發音 (def_zh)
"""

import os
from gtts import gTTS, gTTSError

# --- 根據你的要求，這是包含 definition 和 definition_zh 的完整題庫 ---
word_bank = [
    {"word": "agency", "translation": "代辦處；經銷處；政府機構",
     "sentence": "Many people worked at the agency.",
     "sentence_zh": "許多人在這家代辦處工作。",
     "definition": "If you work at an agency, your job is to help others to get something done.",
     "definition_zh": "如果你在一家代辦處工作，你的工作就是幫助別人完成一些事情。"},
    
    {"word": "business", "translation": "生意；業務；商店",
     "sentence": "My aunt opened a small business that sells coffee.",
     "sentence_zh": "我阿姨開了一家賣咖啡的小店。",
     "definition": "A place open for business is ready to work, buy, or sell something.",
     "definition_zh": "一個開放做生意的地方，就是準備好工作、購買或販售某物的場所。"},
     
    {"word": "confidently", "translation": "自信地；有信心地",
     "sentence": "Tia confidently stood up to give her report.",
     "sentence_zh": "Tia 自信地站起來做報告。",
     "definition": "When you do something confidently, you are sure you will do it well.",
     "definition_zh": "當你自信地做某事時，你確信自己能做得很好。"},
     
    {"word": "eagerly", "translation": "熱切地；渴望地",
     "sentence": "The family eagerly explored their new home.",
     "sentence_zh": "這家人熱切地探索他們的新家。",
     "definition": "When you do something eagerly, you really want to do it.",
     "definition_zh": "當你熱切地做某事時，你真的很想做它。"},
     
    {"word": "seeps", "translation": "滲出；緩慢穿過",
     "sentence": "The sand seeps through the hourglass.",
     "sentence_zh": "沙子緩慢地從沙漏中滲出。",
     "definition": "When something seeps, it passes slowly through a small opening.",
     "definition_zh": "當某物滲出時，它會緩慢地穿過一個小開口。"},
     
    {"word": "mystery", "translation": "謎；難以理解的事物",
     "sentence": "The contents of the box are a mystery.",
     "sentence_zh": "箱子裡的內容物是個謎。",
     "definition": "A mystery is something that is hard to understand or is not known about.",
     "definition_zh": "謎是難以理解或不為人知的事物。"},
     
    {"word": "ace", "translation": "高手；一流人才",
     "sentence": "He is an ace athlete.",
     "sentence_zh": "他是一位一流的運動員。",
     "definition": "Someone described as an ace is extremely good at something.",
     "definition_zh": "被描述為高手的人，在某方面是非常優秀的。"},
     
    {"word": "located", "translation": "位於；坐落於",
     "sentence": "The alligator pond was located near the center of the zoo.",
     "sentence_zh": "鱷魚池位於動物園的中心附近。",
     "definition": "Where something is located is where it is.",
     "definition_zh": "某物被定位（located）的地方就是它所在的位置。"},
]
# -------------------------------------------------------------------

AUDIO_DIR = "audio"  # mp3 會存放在 ./audio 資料夾


def main():
    print("=== make_audio_files.py 開始執行 ===")
    print("將為題庫中的單字產生：單字 / 英文例句 / 中文例句 / 英文定義 / 中文定義 的 mp3 檔案...\n")

    # 確保 audio 資料夾存在
    os.makedirs(AUDIO_DIR, exist_ok=True)
    print(f"已確認/建立資料夾: {AUDIO_DIR}")
    print("-" * 40)

    for idx, item in enumerate(word_bank, start=1):
        word = item["word"]
        sentence_tpl = item["sentence"]
        sentence_zh = item["sentence_zh"]
        definition_en = item["definition"]     # 【新增】取出英文定義
        definition_zh = item["definition_zh"]   # 【新增】取出中文定義

        # 這裡保留替換邏輯，以防 'sentence' 欄位未來使用 '???' 佔位符
        sentence_en = sentence_tpl.replace("???", word)

        # 檔名前加上編號，方便辨識順序與避免重複 close 被覆蓋
        base = f"{idx:02d}_{word}"

        paths = {
            "word_en": os.path.join(AUDIO_DIR, f"{base}_word_en.mp3"),
            "sent_en": os.path.join(AUDIO_DIR, f"{base}_sent_en.mp3"),
            "sent_zh": os.path.join(AUDIO_DIR, f"{base}_sent_zh.mp3"),
            "def_en": os.path.join(AUDIO_DIR, f"{base}_def_en.mp3"), # 【新增】英文定義路徑
            "def_zh": os.path.join(AUDIO_DIR, f"{base}_def_zh.mp3"), # 【新增】中文定義路徑
        }

        print(f"[{idx:02d}] 單字: {word}")
        print(f"    英文句子: {sentence_en}")
        print(f"    中文句子: {sentence_zh}")
        print(f"    英文定義: {definition_en}") # 【新增】列印英文定義
        print(f"    中文定義: {definition_zh}") # 【新增】列印中文定義

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

        # 4) 【新增】英文定義發音 (def_en)
        try:
            print(f"    ▶ 產生英文定義音檔: {paths['def_en']} ...", end="", flush=True)
            tts_def_en = gTTS(text=definition_en, lang="en")
            tts_def_en.save(paths["def_en"])
            print(" OK")
        except gTTSError as e:
            print(" 失敗（gTTSError）：", e)
        except Exception as e:
            print(" 失敗（其他錯誤）：", e)

        # 5) 【新增】中文定義發音 (def_zh)
        try:
            print(f"    ▶ 產生中文定義音檔: {paths['def_zh']} ...", end="", flush=True)
            tts_def_zh = gTTS(text=definition_zh, lang="zh-TW")
            tts_def_zh.save(paths["def_zh"])
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