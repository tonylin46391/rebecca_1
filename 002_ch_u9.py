import streamlit as st
import datetime
import pandas as pd
# 引入 os 用來檢查本地音檔路徑
import os 
# 引入 gTTS 來生成語音，以及 io 來處理音訊數據流
from gtts import gTTS
import io
# 引入 time 用來控制停頓
import time

# 你的中文詞彙列表
chinese_words = [
    "大象", "曹操", "粗心", "大腿", "秤重",
    "砍樹", "部分", "搖頭", "幾天", "曹沖",
    "首先", "牽手", "下沉", "多少", "沿路",
    "然後", "最後", "年紀", "竟然", "方法"
]

# --- 重新建構 word_bank (只保留詞彙和翻譯) ---
word_bank = []
for word in chinese_words:
    # 只保留 word 和 translation
    word_item = {
        "word": word,               # 測驗用的「詞彙」
        "translation": word,        # 中文翻譯 (與詞彙相同)
    }
    word_bank.append(word_item)


# --- 播放函式 (處理本地檔案 - 專門用於音效) ---
def play_local_audio(filename: str):
    """
    播放本地音效檔案 (例如：正確/錯誤音)，不進行檔案存在檢查。
    注意：你需要將 'audio/duolingo_style_correct.mp3' 和 'audio/dong_dong.mp3' 
    放在你的 Streamlit 專案的 'audio' 資料夾中。
    """
    try:
        # 讀取檔案為 bytes 並讓 Streamlit 播放
        audio_bytes = open(filename, 'rb').read()
        
        # 使用 st.empty() 容器來避免佔用頁面佈局，並設定 autoplay=True
        placeholder = st.empty()
        with placeholder:
            st.audio(audio_bytes, format='audio/mp3', autoplay=True)
            
    except FileNotFoundError:
        # 這裡會提醒使用者如果找不到音效檔案
        st.warning(f"⚠ 找不到音效檔案：'{filename}'，請確認檔案路徑。")
    except Exception as e:
        st.error(f"播放本地音效時發生錯誤：{e}")


# --- 播放函式 (處理 gTTS) ---

def set_gtts_to_play(text: str, lang: str):
    """
    將要播放的 gTTS 內容儲存到 Session State 中，並觸發重新執行。
    """
    if text:
        st.session_state.gtts_to_play = (text, lang)
        st.rerun() # 立即重新執行，在頁面頂部播放
    else:
        st.warning("⚠ 播放內容為空，無法生成語音。")
        
def centralized_gtts_playback():
    """
    在頁面頂部集中處理 gTTS 音訊播放。
    """
    if st.session_state.gtts_to_play is not None:
        text, lang = st.session_state.gtts_to_play
        st.session_state.gtts_to_play = None # 播放前清除狀態
        
        placeholder = st.empty() 
        
        try:
            tts = gTTS(text=text, lang=lang)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            
            with placeholder:
                st.audio(fp, format="audio/mp3", autoplay=True)
            
        except Exception as e:
            st.error(f"生成語音時發生錯誤：{e}")


# --- 初始化 Session State ---
total_questions = len(word_bank)
current_word_hash = hash(tuple(item['word'] for item in word_bank)) 

if "word_bank_hash" not in st.session_state or st.session_state.word_bank_hash != current_word_hash:
    st.session_state.wrong_queue = []
    st.session_state.study_mode = 'LEARNING' 
    st.session_state.sequence_cursor = 0
    st.session_state.current_display_index = 0
    st.session_state.stats = [{"正確": 0, "錯誤": 0} for _ in range(total_questions)]
    st.session_state.history = []
    st.session_state.word_bank_hash = current_word_hash
    st.session_state.last_message = ""      
    st.session_state.gtts_to_play = None    
    st.session_state.local_sound_to_play = "" 
    st.toast("新題庫已載入！")
else:
    if "last_message" not in st.session_state:
        st.session_state.last_message = ""
    if "gtts_to_play" not in st.session_state:
        st.session_state.gtts_to_play = None
    if "local_sound_to_play" not in st.session_state:
        st.session_state.local_sound_to_play = ""


# --- 邏輯控制函式 (保持不變) ---

def go_next_question():
    """
    更新狀態以指向下一題。
    """
    
    # 邏輯 A: 複習模式 (Review Mode)
    if st.session_state.study_mode == 'REVIEW':
        if len(st.session_state.wrong_queue) > 0:
            next_idx = st.session_state.wrong_queue[0]
            st.session_state.current_display_index = next_idx
        else:
            # 錯題都複習完了 -> 回到新一輪
            st.session_state.study_mode = 'LEARNING'
            st.session_state.sequence_cursor = 0
            st.session_state.last_message = "🎉 錯題複習完畢！開始新的一輪！"
            st.session_state.current_display_index = 0
    
    # 邏輯 B: 順序學習模式 (Learning Mode)
    elif st.session_state.study_mode == 'LEARNING':
        
        st.session_state.sequence_cursor += 1
        
        if st.session_state.sequence_cursor < total_questions:
            st.session_state.current_display_index = st.session_state.sequence_cursor
        
        else:
            # --- 處理一輪結束 ---
            
            if len(st.session_state.wrong_queue) > 0:
                st.session_state.study_mode = 'REVIEW'
                st.session_state.last_message = "🔄 一輪結束，進入錯題複習模式！"
                go_next_question()
            else:
                st.session_state.sequence_cursor = 0
                st.session_state.current_display_index = 0
                st.session_state.last_message = "💯 太強了！全部答對，直接開始新的一輪！"


# --- 介面顯示 ---

# 確保一開始有題目
current_index = st.session_state.current_display_index
current_item = word_bank[current_index]

# 取出資料
current_word = current_item["word"]
translation = current_item["translation"]
# 已刪除例句與定義


# --- 標題與狀態顯示 ---
st.markdown("<p style='font-size:22px'><b>🎧 中文詞彙發音練習</b></p>", unsafe_allow_html=True) 

# *** 頁面頂部：集中播放音效 (本地檔案 - 專門用於正確/錯誤提示音) ***
if st.session_state.local_sound_to_play:
    play_local_audio(st.session_state.local_sound_to_play)
    st.session_state.local_sound_to_play = ""

# *** 頁面頂部：集中播放音效 (gTTS) ***
centralized_gtts_playback()


# 顯示最新的結果訊息
if st.session_state.last_message:
    message = st.session_state.last_message
    
    font_size = "24px" 
    
    # 檢查是否為正確或錯誤的訊息
    is_correct_msg = "答對了" in message or "複習完畢" in message or "全部答對" in message
    is_wrong_msg = "答錯" in message or "跳過" in message or "🔄" in message
    
    # 圖片邏輯已移至下方按鈕區塊
    
    if is_correct_msg: 
        display_message = message.replace("✅ ", "").replace("🎉 ", "").replace("💯 ", "")

        html_content = f"""
        <div style="background-color: #e6ffed; border-radius: 0.25rem; padding: 1rem; border-left: 0.5rem solid #090; color: #000;">
            <span style="font-size: {font_size};">✅ {display_message}</span> 
        </div>
        """
        st.markdown(html_content, unsafe_allow_html=True)
        
    elif is_wrong_msg:
        
        display_message = message.replace("❌ ", "").replace("⏭️ ", "").replace("🔄 ", "")
        
        html_content = f"""
        <div style="background-color: #ffeaea; border-radius: 0.25rem; padding: 1rem; border-left: 0.5rem solid #f00; color: #000;">
            <span style="font-size: {font_size};">❌ {display_message}</span>
        </div>
        """
        st.markdown(html_content, unsafe_allow_html=True)

    else:
        st.info(message)
    
    st.session_state.last_message = ""
        
# --- 狀態模式顯示 ---
if st.session_state.study_mode == 'REVIEW':
    st.warning(f"🔥 錯題複習模式 (剩餘 {len(st.session_state.wrong_queue)} 題)")
else:
    display_progress = st.session_state.sequence_cursor 
    if display_progress == total_questions: display_progress = 0
    st.info(f"📖 順序學習模式 (進度 {display_progress + 1} / {total_questions})")


# --- Dolingo 圖片與按鈕區塊 ---

# *** 調整佈局：將圖片置中，並將按鈕放在下一行 (或緊跟在圖片後) ***
# 圖片置中：使用 1:1:1 欄位比例
col_left, col_img, col_right = st.columns([1, 1, 1])

# 圖片顯示在中間欄位
with col_img:
    try:
        # 取得目前程式碼所在的資料夾路徑
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 組合出圖片的完整路徑
        image_path = os.path.join(current_dir, "Dolingo.jpg")
        
        # 顯示圖片
        st.image(image_path, width=100)
    except Exception as e:
        # 如果找不到圖片，印出錯誤訊息方便除錯
        print(f"圖片讀取錯誤: {e}")
        pass 
        

# 按鈕區塊 (讓按鈕自己佔據整個寬度)
st.markdown("""
    <style>
    div.stButton > button {
        /* 調整按鈕的最小寬度 */
        min-width: 100%;
        /* 調整文字大小 */
        font-size: 24px; 
        /* 調整內距（上下左右），讓按鈕更厚實 */
        padding: 15px 10px; 
        /* 調整按鈕的圓角 */
        border-radius: 10px;
        
        /* --- 顏色修改 (橘色) --- */
        background-color: #FF9900; 
        color: #FFFFFF; 
        border: 1px solid #FF9900; 
    }
    
    /* 增加滑鼠懸停 (hover) 效果 */
    div.stButton > button:hover {
        background-color: #FFAA33; 
        border: 1px solid #FFAA33;
    }
    
    /* *** 移除舊的 CSS 對齊調整，讓圖片自由放在上方 *** */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) div.stImage {
        margin-top: 0px !important; 
    }
    
    </style>
    """, unsafe_allow_html=True)
    
# 按鈕邏輯
if st.button("▶ 圈詞測試下一題"): 
    # 播放詞彙 (中文 'zh-tw')
    set_gtts_to_play(current_word, 'zh-tw') 


# --- 單字答題表單 ---
input_key = f"input_{current_index}_{st.session_state.study_mode}" 

with st.form(key=f"form_{current_index}", clear_on_submit=True):
    # 確保這裡的提示是中文
    user_input = st.text_input("請輸入你聽到的中文詞彙 (輸入完按 Enter 即可)", key=input_key, autocomplete="off")
    submitted = st.form_submit_button("提交答案 (或按 Enter)")
    
    if submitted:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_text = user_input.strip()
        # 中文比對不需要 lower()
        is_correct = (user_text == current_word) 

        # --- 答案處理與狀態更新 ---
        
        if is_correct:
            st.session_state.stats[current_index]["正確"] += 1
            st.session_state.last_message = "✅ 答對了！" 
            if current_index in st.session_state.wrong_queue:
                st.session_state.wrong_queue.remove(current_index) 
            
            # *** 設定正確音效路徑 ***
            st.session_state.local_sound_to_play = "audio/duolingo_style_correct.mp3" 
            
            go_next_question()

        else:
            st.session_state.stats[current_index]["錯誤"] += 1
            msg = f"❌ 答錯！正確答案是：{current_word}" if user_text else f"⏭️ 跳過！正確答案是：{current_word}"
            st.session_state.last_message = msg 
            
            if current_index not in st.session_state.wrong_queue:
                st.session_state.wrong_queue.append(current_index) 
            
            if st.session_state.study_mode == 'REVIEW' and current_index in st.session_state.wrong_queue:
                if st.session_state.wrong_queue[0] == current_index:
                    item = st.session_state.wrong_queue.pop(0)
                    st.session_state.wrong_queue.append(item)
            
            # *** 設定錯誤音效路徑 ***
            st.session_state.local_sound_to_play = "audio/dong_dong.mp3" 

            go_next_question()


        # 紀錄歷史
        st.session_state.history.append({
            "模式": "複習" if st.session_state.study_mode == 'REVIEW' else "一般",
            "題號": current_index + 1,
            "詞彙": current_word,
            "輸入": user_input,
            "結果": "正確" if is_correct else "錯誤",
            "時間": now_str
        })

        st.rerun() 

# --- 側邊欄統計 (保持不變) ---
st.sidebar.header("📊 練習進度統計")
st.sidebar.write(f"目前模式：**{st.session_state.study_mode}**")
st.sidebar.write(f"待複習錯題數：{len(st.session_state.wrong_queue)}")

st.sidebar.subheader("📈 詞彙答題統計")
stats_list = []
for i, item in enumerate(word_bank):
    s = st.session_state.stats[i]
    total_try = s["正確"] + s["錯誤"]
    rate = f"{s['正確']}/{total_try}" if total_try > 0 else "0/0"
    
    # --- 狀態燈邏輯 ---
    status_light = "⚪" 
    
    if i in st.session_state.wrong_queue:
        status_light = "🔴" 
    
    elif s["正確"] > 0:
        status_light = "🟢" 
    
    elif s["錯誤"] > 0 and s["正確"] == 0:
        status_light = "🟡" 
        
    stats_list.append({
        "狀態": status_light,
        "題號": i + 1,
        "詞彙": item["word"],
        "正確率": rate
    })
st.sidebar.dataframe(pd.DataFrame(stats_list), use_container_width=True)

st.sidebar.subheader("📝 歷史紀錄")
if st.session_state.history:
    st.sidebar.dataframe(pd.DataFrame(st.session_state.history[::-1]), use_container_width=True)