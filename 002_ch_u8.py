import streamlit as st
import os
import datetime
import pandas as pd

# 題庫
words = [
    "小熊", "口渴", "烏鴉", "喝水", "方法",
    "森林", "動物", "知道", "聰明", "旅行",
    "中午", "裝扮", "小瓶子", "許多", "石頭",
    "動作", "難道", "忘記", "哈哈", "但是"
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
    檔名規則：audio/<單字>.mp3
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
            # 由於下一輪開始前，st.rerun() 會再次運行，這裡需要處理下一輪的第一個詞
            return words[st.session_state.index]

    # normal 模式 → 按順序走題庫
    if st.session_state.index < len(words):
        return words[st.session_state.index]
    else:
        # 一輪結束 → 準備錯題複習
        # 這裡使用 st.session_state.answered 來判斷哪些是錯題（值為 False）
        wrongs = [w for w, ans in st.session_state.answered.items() if ans is False]
        if wrongs:
            st.session_state.mode = "review"
            # 刷新 retry_queue
            st.session_state.retry_queue = wrongs.copy()
            st.session_state.last_result = "🔁 進入錯題複習！"
            return st.session_state.retry_queue[0]
        else:
            # 全部答對 → 新一輪
            st.session_state.index = 0
            st.session_state.answered = {} # 重設 answered 狀態
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
            st.session_state.answered[current_word] = True # 標記為正確
            
        # 如果在 normal 模式答對，則需要檢查它是否還在 retry_queue，如果是，代表它在上一輪錯過，這次答對了，可以移出。
        # 但因為 retry_queue 只在 review 模式才被使用，且 answered[word]=True 優先，所以這裡保持不變動。
        
    else:
        st.session_state.stats[current_word]["錯誤"] += 1
        result = "錯誤"
        st.session_state.last_result = f"❌ 答錯！正確答案是：**{current_word}**" # 提示正確答案

        if st.session_state.mode == "review":
            # 複習模式答錯 → 將該詞移到隊列尾端，稍後再問
            st.session_state.retry_queue.remove(current_word)
            st.session_state.retry_queue.append(current_word)
        else:
            # normal 模式答錯 → 標記為錯誤
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

    # reset 播放並強制刷新頁面
    st.session_state.played = False
    st.session_state.last_word = None
    st.rerun() # 提交後強制跳下一題

# 輸入表單
with st.form(key=f"form_{current_word}", clear_on_submit=True): # clear_on_submit=True，讓輸入框自動清空
    st.text_input("請輸入你聽到的『中文字』：",
                   key=input_key,
                   autocomplete="off")
    st.form_submit_button("提交答案 (或按 Enter)", on_click=submit_answer)

# 側邊欄進度
st.sidebar.header("📊 學習進度")
done = sum(1 for v in st.session_state.answered.values() if v is True)
total = len(words)
st.sidebar.write(f"✅ 已正確答對：{done} / {total}")
st.sidebar.write(f"🔄 待複習錯題：{len(st.session_state.retry_queue)}")
st.sidebar.write(f"模式：**{st.session_state.mode.upper()}**")

# 答題歷史
st.sidebar.header("📝 答題歷史")
if st.session_state.history:
    # 倒序顯示，最新的在最上面
    df = pd.DataFrame(st.session_state.history[::-1])
    st.sidebar.dataframe(df, use_container_width=True)

# 單字正確率統計 + 狀態燈
st.sidebar.header("📊 單字正確率統計")
stats_list = []
for w in words: # 遍歷整個題庫的順序
    s = st.session_state.stats[w]
    total_attempts = s["正確"] + s["錯誤"]
    rate = f"{s['正確']}/{total_attempts}" if total_attempts > 0 else "0/0"
    
    # --- 狀態燈邏輯 ---
    status_light = "⚪" # 預設: 尚未作答 (或還沒進入該輪)
    
    if w in st.session_state.retry_queue:
        status_light = "🔴" # 錯題隊列中
    elif w in st.session_state.answered:
        if st.session_state.answered[w] is True:
            status_light = "🟢" # 已經正確答對過
        elif st.session_state.answered[w] is False:
            # 如果不在 retry_queue 但在 answered 裡是 False，代表它在 normal 模式答錯，
            # 且還沒進入或已離開複習模式 (通常不會發生，因為錯題會加入 queue)
            status_light = "🟡" # 曾答錯，待複習 (用黃色作區分，但主要還是看 retry_queue)
    
    stats_list.append({
        "狀態": status_light,
        "單字": w, 
        "正確/總次數": rate
    })
df_stats = pd.DataFrame(stats_list)
st.sidebar.dataframe(df_stats, use_container_width=True)