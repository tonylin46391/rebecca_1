import streamlit as st
from gtts import gTTS, gTTSError   # 多匯入 gTTSError 方便抓錯
from io import BytesIO            # 比直接用 io.BytesIO 好讀
import datetime
import pandas as pd


# 題庫
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



# 初始化 session state
if "index" not in st.session_state:
    st.session_state.index = 0
if "mode" not in st.session_state:  # normal / review
    st.session_state.mode = "normal"
if "retry_queue" not in st.session_state:
    st.session_state.retry_queue = []
if "answered" not in st.session_state:
    st.session_state.answered = {}
if "history" not in st.session_state:
    st.session_state.history = []
if "stats" not in st.session_state:
    st.session_state.stats = {w: {"正確": 0, "錯誤": 0} for w in words}
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "played" not in st.session_state:
    st.session_state.played = False
if "last_word" not in st.session_state:
    st.session_state.last_word = None

st.markdown('<p style="font-size:26px">🎧 聽音辨字練習</p>', unsafe_allow_html=True)


# ✅ 安全版 TTS 函式：加上錯誤處理 & 語言代碼用 zh-tw
def generate_tts(word: str, lang: str = "zh-tw"):
    """使用 gTTS 產生語音並在畫面播放。"""
    word = (word or "").strip()
    if not word:
        st.warning("沒有可以轉語音的文字。")
        return

    try:
        # 建立 gTTS 物件
        tts = gTTS(text=word, lang=lang)

        # 用 BytesIO 存在記憶體
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)

        # 直接把 BytesIO 丟給 st.audio
        st.audio(fp, format="audio/mp3")

    except gTTSError:
        # 這類錯誤通常是：網路問題、被 Google 擋、呼叫太頻繁…
        st.error("🔊 語音服務目前發生問題（gTTSError）。\n"
                 "可能是網路不穩或呼叫過於頻繁，請稍後再試一次。")
    except Exception as e:
        # 其他預期外錯誤
        st.error(f"產生語音時發生未預期錯誤：{e}")


# 📌 取得下一個題目
def get_next_word():
    # 優先處理錯題 queue
    if st.session_state.mode == "review":
        if st.session_state.retry_queue:
            return st.session_state.retry_queue[0]
        else:
            # 錯題複習結束 → 回到新一輪
            st.session_state.mode = "normal"
            st.session_state.index = 0
            st.session_state.last_result = "🎉 錯題複習完成！開始新一輪！"
            return words[st.session_state.index]

    # normal 模式 → 按順序走題庫
    if st.session_state.index < len(words):
        return words[st.session_state.index]
    else:
        # 一輪結束 → 準備錯題複習
        wrongs = [w for w, ans in st.session_state.answered.items() if ans is False]
        if wrongs:
            st.session_state.mode = "review"
            st.session_state.retry_queue = wrongs.copy()
            st.session_state.last_result = "🔁 進入錯題複習！"
            return st.session_state.retry_queue[0]
        else:
            # 全部答對 → 新一輪
            st.session_state.index = 0
            st.session_state.answered = {}
            st.session_state.last_result = "🎉 全部正確！開始新一輪！"
            return words[st.session_state.index]


# 取得目前題目
current_word = get_next_word()
input_key = f"input_{current_word}_{st.session_state.index}_{st.session_state.mode}"

# 🔊 自動播放音訊（只在新題目時播放一次）
if (not st.session_state.played) or (st.session_state.last_word != current_word):
    generate_tts(current_word)
    st.session_state.played = True
    st.session_state.last_word = current_word

# 顯示最新答題結果訊息
if st.session_state.last_result:
    st.info(st.session_state.last_result)


# 提交答案
def submit_answer():
    user_input = st.session_state.get(input_key, "")
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user_input == current_word:
        st.session_state.stats[current_word]["正確"] += 1
        result = "正確"
        st.session_state.last_result = "✅ 答對了！"

        # 複習模式 → 答對後移出 queue
        if st.session_state.mode == "review":
            if current_word in st.session_state.retry_queue:
                st.session_state.retry_queue.remove(current_word)
        else:
            st.session_state.answered[current_word] = True
    else:
        st.session_state.stats[current_word]["錯誤"] += 1
        result = "錯誤"
        st.session_state.last_result = f"❌ 答錯！正確答案是：{current_word}"

        if st.session_state.mode == "review":
            # 答錯 → 保留在 queue
            pass
        else:
            st.session_state.answered[current_word] = False

    # 紀錄歷史
    st.session_state.history.append({
        "題目": current_word,
        "結果": result,
        "學生輸入的答案": user_input,
        "時間": now_str
    })

    # normal 模式 → 下一題
    if st.session_state.mode == "normal":
        st.session_state.index += 1

    # reset 播放，讓下一題會重新播音
    st.session_state.played = False
    st.session_state.last_word = None


# 📝 輸入表單
with st.form(key=f"form_{current_word}", clear_on_submit=False):
    st.text_input("請輸入你聽到的『中文字』：",  # 這裡改成中文字
                  key=input_key,
                  autocomplete="off")
    st.form_submit_button("提交答案", on_click=submit_answer)

# 📊 側邊欄進度
st.sidebar.header("📊 學習進度")
done = sum(1 for v in st.session_state.answered.values() if v is True)
total = len(words)
st.sidebar.write(f"✅ 已正確答對：{done} / {total}")

# 📝 答題歷史
st.sidebar.header("📝 答題歷史")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.sidebar.dataframe(df, use_container_width=True)

# 📊 單字正確率統計
st.sidebar.header("📊 單字正確率統計")
stats_list = []
for w, s in st.session_state.stats.items():
    total_attempts = s["正確"] + s["錯誤"]
    rate = f"{s['正確']}/{total_attempts}" if total_attempts > 0 else "0/0"
    stats_list.append({"單字": w, "正確/總次數": rate})
df_stats = pd.DataFrame(stats_list)
st.sidebar.dataframe(df_stats, use_container_width=True)
