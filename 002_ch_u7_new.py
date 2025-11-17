import streamlit as st
import os
import datetime
import pandas as pd

# 題庫
words = [ 
    "神奇",
	"點頭",
	"看得見",
	"真漂亮",
    "開開心心",
    "大街上",
    "滿街的人",
    "張大雙眼",
    "看哪看",
    "左思右想",
    "胖國王",
    "衣裳",
    "一針一線",
    "簡單",
    "聰明",
    "大臣",
    "不敢說",
    "東西",
    "慌張",
    "一直",
    "好棒"
]

# 音檔所在資料夾（請在專案下建立 audio 資料夾，放入對應 mp3）
AUDIO_DIR = "audio"

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

st.markdown('<p style="font-size:26px">🎧 聽音辨字練習（預載 mp3 版本）</p>', unsafe_allow_html=True)


# ✅ 播放「預先準備好的 mp3」的函式（不再使用 gTTS）
def play_preloaded_audio(word: str) -> bool:
    """
    播放對應單字的本地 mp3 檔案。
    檔名規則：audio/小鎮.mp3、audio/柿餅.mp3 ...
    回傳 True = 播放成功；False = 找不到檔案或讀取失敗。
    """
    word = (word or "").strip()
    if not word:
        st.warning("沒有可以播放的文字。")
        return False

    # 檔名：audio/<單字>.mp3
    filename = os.path.join(AUDIO_DIR, f"{word}.mp3")

    if not os.path.exists(filename):
        st.warning(f"⚠️ 找不到音檔：{filename}，請確認檔案是否存在。")
        return False

    try:
        with open(filename, "rb") as f:
            audio_bytes = f.read()
        st.audio(audio_bytes, format="audio/mp3")
        return True
    except Exception as e:
        st.error(f"讀取音檔時發生錯誤：{e}")
        return False


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

# 🔊 自動播放音訊（只有在新題目，或尚未播放成功時才播）
if (not st.session_state.played) or (st.session_state.last_word != current_word):
    ok = play_preloaded_audio(current_word)
    st.session_state.played = ok      # 只有成功才標記已播放
    st.session_state.last_word = current_word if ok else None

# 顯示最新答題結果訊息
if st.session_state.last_result:
    st.info(st.session_state.last_result)


# 提交答案
def submit_answer():
    user_input = st.session_state[input_key]
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
        st.session_state.last_result = "❌ 答錯！"

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

    # reset 播放
    st.session_state.played = False
    st.session_state.last_word = None


# 輸入表單
with st.form(key=f"form_{current_word}", clear_on_submit=False):
    st.text_input("請輸入你聽到的『中文字』：",
                  key=input_key,
                  autocomplete="off")
    st.form_submit_button("提交答案", on_click=submit_answer)

# 側邊欄進度
st.sidebar.header("📊 學習進度")
done = sum(1 for v in st.session_state.answered.values() if v is True)
total = len(words)
st.sidebar.write(f"✅ 已正確答對：{done} / {total}")

# 答題歷史
st.sidebar.header("📝 答題歷史")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.sidebar.dataframe(df, use_container_width=True)

# 單字正確率統計
st.sidebar.header("📊 單字正確率統計")
stats_list = []
for w, s in st.session_state.stats.items():
    total_attempts = s["正確"] + s["錯誤"]
    rate = f"{s['正確']}/{total_attempts}" if total_attempts > 0 else "0/0"
    stats_list.append({"單字": w, "正確/總次數": rate})
df_stats = pd.DataFrame(stats_list)
st.sidebar.dataframe(df_stats, use_container_width=True)
