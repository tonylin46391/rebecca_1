import streamlit as st
import os
import datetime
import pandas as pd
import time 

# 題庫
words = [
    "小熊", "口渴", "烏鴉", "喝水", "方法",
    "森林", "動物", "知道", "聰明", "旅行",
    "中午", "裝扮", "小瓶子", "許多", "石頭",
    "動作", "難道", "忘記", "哈哈", "但是"
]


# 音檔所在資料夾（請在專案下建立 audio 資料夾，放入對應 mp3）
AUDIO_DIR = "audio"

# 答對/答錯 音效檔名（請在 audio 資料夾放入 correct.mp3 和 wrong.mp3）
CORRECT_SOUND_FILE = os.path.join(AUDIO_DIR, "correct.mp3")
WRONG_SOUND_FILE = os.path.join(AUDIO_DIR, "wrong.mp3")


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
# 控制「繼續下一題」按鈕顯示的狀態 (Duolingo 流程的核心)
if "show_next" not in st.session_state: 
    st.session_state.show_next = False
# 📢 【保留】用於儲存待播放音效的 bytes (確保音效可靠播放)
if "sound_to_play" not in st.session_state: 
    st.session_state.sound_to_play = None 


st.markdown('<p style="font-size:26px">🎧 聽音辨字練習（預載 mp3 版本）</p>', unsafe_allow_html=True)


# ✅ 播放「預先準備好的 mp3」的函式
def play_preloaded_audio(word: str) -> bool:
    """
    播放對應單字的本地 mp3 檔案。
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


# 📢 【修改】通用播放音效的函式，改為將檔案 bytes 存入 session_state (這是可靠播放的關鍵)
def play_sound(filepath: str):
    """
    通用播放音效的函式，將音效內容儲存到 session_state 待主腳本播放。
    """
    if not os.path.exists(filepath):
        st.error(f"❌ 嚴重錯誤：找不到音效檔！請確認檔案路徑是否正確：{filepath}")
        return

    try:
        with open(filepath, "rb") as f:
            audio_bytes = f.read()
        
        # 儲存音效 bytes 到 session state，等待主腳本執行時播放
        st.session_state.sound_to_play = audio_bytes

    except Exception as e:
        st.error(f"讀取音效檔時發生錯誤：{e}")


def play_correct_sound():
    """播放答對音效"""
    play_sound(CORRECT_SOUND_FILE)


def play_wrong_sound():
    """播放答錯音效"""
    play_sound(WRONG_SOUND_FILE)


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
# 確保輸入框的 key 在每次題目變換時是唯一的
input_key = f"input_{current_word}_{st.session_state.index}_{st.session_state.mode}" 


# 📢 檢查並播放待播放的音效 (在最上方執行，優先播放)
if st.session_state.sound_to_play is not None:
    st.audio(st.session_state.sound_to_play, format="audio/mp3", autoplay=True)
    # 立即清除，確保下次運行不會重複播放
    st.session_state.sound_to_play = None


# 🔊 自動播放音訊（只有在新題目，或尚未播放成功時才播）
if (not st.session_state.played) or (st.session_state.last_word != current_word):
    # 只有在非結果頁（即 show_next=False）才自動播放
    if not st.session_state.show_next:
        ok = play_preloaded_audio(current_word)
        st.session_state.played = ok      # 只有成功才標記已播放
        st.session_state.last_word = current_word if ok else None

# 顯示最新答題結果訊息 (Duolingo 風格：結果顯示)
if st.session_state.last_result:
    st.markdown(st.session_state.last_result, unsafe_allow_html=True)

# 處理點擊「繼續下一題」按鈕的邏輯
def go_to_next_question():
    """處理點擊「繼續下一題」按鈕的邏輯，強制頁面跳轉。"""
    st.session_state.show_next = False # 隱藏結果區
    # 如果是答錯，我們不需要推進 index，題目會停留在 current_word (因為 index 沒有動)
    # 如果是答對，submit_answer 已經推進了 index
    st.rerun() # 觸發跳轉到下一題或重新載入當前題目

# 提交答案
def submit_answer():
    user_input = st.session_state[input_key]
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user_input == current_word:
        st.session_state.stats[current_word]["正確"] += 1
        result = "正確"
        
        # 🔊 播放答對音效
        play_correct_sound()
        
        # 設置結果訊息 (Duolingo 風格)
        st.session_state.last_result = '<p style="font-size:36px; color:green; font-weight:bold;">✅ 答對了！</p>' 

        # 複習模式 → 答對後移出 queue
        if st.session_state.mode == "review":
            if current_word in st.session_state.retry_queue:
                st.session_state.retry_queue.remove(current_word)
        else:
            st.session_state.answered[current_word] = True # 標記為正確
        
        # 答對了才推進 index
        if st.session_state.mode == "normal":
            st.session_state.index += 1
        
    else:
        st.session_state.stats[current_word]["錯誤"] += 1
        result = "錯誤"
        
        # 🔊 播放答錯音效
        play_wrong_sound()
        
        # 設置結果訊息 (Duolingo 風格)
        st.session_state.last_result = f'<p style="font-size:36px; color:red; font-weight:bold;">❌ 答錯！</p>正確答案是：**{current_word}**'

        if st.session_state.mode == "review":
            # 複習模式答錯 → 將該詞移到隊列尾端，稍後再問
            if current_word in st.session_state.retry_queue:
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

    # reset 播放狀態，並設定顯示「繼續下一題」按鈕 (Duolingo 風格)
    st.session_state.played = False
    st.session_state.last_word = None
    st.session_state.show_next = True # 設定旗標，讓「繼續下一題」按鈕出現
    # 這裡不再有 st.rerun()，腳本會繼續執行並停在結果頁面

# 根據狀態顯示輸入表單或「繼續下一題」按鈕 (Duolingo 風格：切換畫面)
if st.session_state.show_next:
    # 顯示 Duolingo 風格的「繼續」按鈕
    button_label = "👉 繼續下一題" if st.session_state.last_result and "✅ 答對了" in st.session_state.last_result else "再試一次"
    st.button(button_label, on_click=go_to_next_question)
    
else:
    # 顯示輸入表單
    with st.form(key=f"form_{current_word}", clear_on_submit=True):
        st.text_input("請輸入你聽到的『中文字』：",
                       key=input_key,
                       autocomplete="off")
        # 提交答案後，會執行 submit_answer，並設定 show_next = True
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
            # 且還沒進入或已離開複習模式 (主要看 retry_queue)
            status_light = "🟡" # 曾答錯，待複習 
    
    stats_list.append({
        "狀態": status_light,
        "單字": w, 
        "正確/總次數": rate
    })
df_stats = pd.DataFrame(stats_list)
st.sidebar.dataframe(df_stats, use_container_width=True)