import streamlit as st
import datetime
import pandas as pd
# 引入 os 用來檢查本地音檔路徑
import os 
# 引入 gTTS 來生成語音，以及 io 來處理音訊數據流
from gtts import gTTS
import io
# 【新增】引入 difflib 進行字串差異比對
import difflib 
# 【新增】引入 re 進行正規表達式處理
import re 

# --- 【修正】自定義 CSS 樣式 (調整按鈕文字和大小) ---
st.markdown("""
<style>
/* 由於此 CSS 選擇器 (div.stButton > button) 會影響頁面上所有 Streamlit 按鈕 */
div.stButton > button {
    /* 調整按鈕的最小寬度 */
    min-width: 100%;
    /* 🌟 修正點 1: 縮小文字大小 */
    font-size: 20px; 
    /* 🌟 修正點 2: 縮小內距，讓按鈕變窄一點 */
    padding: 10px 5px; 
    /* 調整按鈕的圓角 */
    border-radius: 18px;
    
    /* --- 顏色修改 (橘色) --- */
    background-color: #FF9900 !important; 
    color: #FFFFFF !important; /* 預設白色文字 */
    border: 1px solid #FF9900 !important; 
}

/* 增加滑鼠懸停 (hover) 效果 */
div.stButton > button:hover {
    /* 懸停時顏色略微變淺 */
    background-color: #FFAA33 !important; 
    border: 1px solid #FFAA33 !important;
    /* 滑鼠懸停時文字顏色變黑色 */
    color: black !important; 
}

/* 增加按鈕按下 (active) 效果 */
div.stButton > button:active {
    /* 按下時顏色略微變深 */
    background-color: #E68A00 !important; 
    border: 1px solid #E68A00 !important; 
    /* 按下時文字顏色維持預設的白色 */
    color: white !important; 
}
    
/* 垂直對齊圖片的 CSS 調整 (保留) */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) div.stImage {
    margin-top: 0px; 
}

</style>
""", unsafe_allow_html=True)

word_bank = [
    {"word": "agency", "translation": "代辦處；經銷處；政府機構",
     "sentence": "Many people worked at the agency.",
     "sentence_zh": "許多人在這家代辦處工作。",
     "definition": "If you work at an agency, your job is to help others to get something done.",
     "definition_zh": "如果你在一家代辦處工作，你的工作就是幫助別人完成一些事情。",
     "blank_index": 5 # agency 是第 6 個單字 (索引 4)
     },
    
    {"word": "business", "translation": "生意；業務；商店",
     "sentence": "My aunt opened a small business that sells coffee.",
     "sentence_zh": "我阿姨開了一家賣咖啡的小店。",
     "definition": "A place open for business is ready to work, buy, or sell something.",
     "definition_zh": "一個開放做生意的地方，就是準備好工作、購買或販售某物的場所。",
     "blank_index": 5 # business 是第 5 個單字 (索引 4)
     },
     
    {"word": "confidently", "translation": "自信地；有信心地",
     "sentence": "Tia confidently stood up to give her report.",
     "sentence_zh": "Tia 自信地站起來做報告。",
     "definition": "When you do something confidently, you are sure you will do it well.",
     "definition_zh": "當你自信地做某事時，你確信自己能做得很好。",
     "blank_index": 1 # confidently 是第 2 個單字 (索引 1)
     },
     
    {"word": "eagerly", "translation": "熱切地；渴望地",
     "sentence": "The family eagerly explored their new home.",
     "sentence_zh": "這家人熱切地探索他們的新家。",
     "definition": "When you do something eagerly, you really want to do it.",
     "definition_zh": "當你熱切地做某事時，你真的很想做它。",
     "blank_index": 2 # eagerly 是第 3 個單字 (索引 2)
     },
     
    {"word": "seeps", "translation": "滲出；緩慢穿過",
     "sentence": "The sand seeps through the hourglass.",
     "sentence_zh": "沙子緩慢地從沙漏中滲出。",
     "definition": "When something seeps, it passes slowly through a small opening.",
     "definition_zh": "當某物滲出時，它會緩慢地穿過一個小開口。",
     "blank_index": 2 # seeps 是第 3 個單字 (索引 2)
     },
     
    {"word": "mystery", "translation": "謎；難以理解的事物",
     "sentence": "The contents of the box are a mystery.",
     "sentence_zh": "箱子裡的內容物是個謎。",
     "definition": "A mystery is something that is hard to understand or is not known about.",
     "definition_zh": "謎是難以理解或不為人知的事物。",
     "blank_index": 7 # mystery. 是第 8 個單字 (索引 7)
     },
     
    {"word": "ace", "translation": "高手；一流人才",
     "sentence": "He is an ace athlete.",
     "sentence_zh": "他是一位一流的運動員。",
     "definition": "Someone described as an ace is extremely good at something.",
     "definition_zh": "被描述為高手的人，在某方面是非常優秀的。",
     "blank_index": 3 # ace 是第 4 個單字 (索引 3)
     },
     
    {"word": "located", "translation": "位於；坐落於",
     "sentence": "The alligator pond was located near the center of the zoo.",
     "sentence_zh": "鱷魚池位於動物園的中心附近。",
     "definition": "Where something is located is where it is.",
     "definition_zh": "某物被定位（located）的地方就是它所在的位置。",
     "blank_index": 4 # located 是第 5 個單字 (索引 4)
     },
]
# --- 播放函式 (處理本地檔案) ---

def play_local_audio(filename: str):
    """
    播放本地上傳的音訊檔案，利用 Streamlit 的 st.audio。
    """
    if not os.path.exists(filename):
        # 由於我們沒有提供實體音效檔，這裡不顯示警告，避免干擾，但保留邏輯
        return
    
    try:
        # 讀取檔案為 bytes 並讓 Streamlit 播放
        audio_bytes = open(filename, 'rb').read()
        
        # 使用 st.empty() 容器來避免佔用頁面佈局
        placeholder = st.empty()
        with placeholder:
            st.audio(audio_bytes, format='audio/mp3', autoplay=True)
            
    except Exception as e:
        st.error(f"播放本地音訊時發生錯誤：{e}")


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
        
        # 使用 st.empty() 容器，播放器會被渲染在頂部且不影響下方佈局
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


# --- 差異化顯示函式 (字元精確對齊) ---
def get_diff_html(a: str, b: str) -> str:
    """
    使用 difflib.SequenceMatcher 進行字元級比對，
    並使用固寬的 HTML span 元素實現精確對齊的差異顯示。
    """
    a = a.lower()
    b = b.lower()
    s = difflib.SequenceMatcher(None, a, b)

    correct = []
    inputed = []

    # 定義樣式
    GREEN = "background:#ddffdd;"
    RED = "background:#b22222;color:white;"
    EMPTY = "background:#eeeeee;color:#888;"

    def span(text, style):
        # 設置固定寬度 (20px) 和等寬字體 (monospace) 確保對齊
        return f"<span style='{style}display:inline-block;width:20px;height:32px;line-height:27px;margin:1px;border-radius:4px;font-family:monospace;text-align:center;font-size:36px;'>{text}</span>"

    for opcode, a1, a2, b1, b2 in s.get_opcodes():
        A = a[a1:a2]
        B = b[b1:b2]

        if opcode == "equal":
            # 相同：兩邊都標綠色
            for x, y in zip(A, B):
                correct.append(span(x, GREEN))
                inputed.append(span(y, GREEN))

        elif opcode == "replace":
            # 替換：兩邊都標深紅色
            L = max(len(A), len(B))
            for i in range(L):
                ca = A[i] if i < len(A) else "_" # 較短的字串用 '_' 填充
                cb = B[i] if i < len(B) else "_"
                correct.append(span(ca, RED))
                inputed.append(span(cb, RED))

        elif opcode == "delete":
            # 刪除 (正確答案有，輸入沒有)：正確答案標深紅色，輸入標灰色 '_'
            for ch in A:
                correct.append(span(ch, RED))
                inputed.append(span("_", EMPTY))

        elif opcode == "insert":
            # 插入 (正確答案沒有，輸入多餘)：正確答案標灰色 '_'，輸入標深紅色
            for ch in B:
                correct.append(span("_", EMPTY))
                inputed.append(span(ch, RED))

    return f"""
    <div style='text-align:center;margin-top:12px;'>
        {''.join(correct)}
        <div style='font-size:13px;margin:3px;'>⬇️</div>
        {''.join(inputed)}
    </div>
    """
# ----------------------------------------

# --- 【新增】挖空例句函式 ---
def get_sentence_with_blank(sentence: str, target_word: str, blank_index: int) -> str:
    """
    將句子中的目標單字替換為空白符號 (_____)，以供填空練習。
    """
    # 將句子分割成單字列表
    words = sentence.split()
    blank = "_____"
    
    if 0 <= blank_index < len(words):
        word_to_blank = words[blank_index]
        
        # 找出結尾標點符號 (如 ., !, ?)
        trailing_punctuation = ""
        if word_to_blank and not word_to_blank[-1].isalnum():
            # 如果最後一個字元不是英文字母或數字，就假設它是標點符號
            trailing_punctuation = word_to_blank[-1]
        
        # 簡單化處理：直接替換 words 列表中的特定位置
        words[blank_index] = blank + trailing_punctuation
        
        return ' '.join(words)

    # 如果索引不正確，則返回原句 (作為安全機制)
    return sentence
# ----------------------------------------


# --- 初始化 Session State ---
total_questions = len(word_bank)
current_word_hash = hash(tuple((item['word'], item.get('definition_zh')) for item in word_bank))

if "word_bank_hash" not in st.session_state or st.session_state.word_bank_hash != current_word_hash:
    st.session_state.wrong_queue = []
    st.session_state.study_mode = 'LEARNING' 
    st.session_state.sequence_cursor = 0
    st.session_state.current_display_index = 0
    st.session_state.stats = [{"正確": 0, "錯誤": 0} for _ in range(total_questions)]
    st.session_state.history = []
    st.session_state.word_bank_hash = current_word_hash
    st.session_state.last_message = ""      # 用於儲存最新的結果訊息
    st.session_state.gtts_to_play = None    # <-- gTTS 播放狀態
    st.session_state.local_sound_to_play = "" # <-- 本地音效播放狀態
    st.toast("新題庫已載入！")
else:
    # 確保所有變數都存在
    if "last_message" not in st.session_state:
        st.session_state.last_message = ""
    if "gtts_to_play" not in st.session_state:
        st.session_state.gtts_to_play = None
    if "local_sound_to_play" not in st.session_state:
        st.session_state.local_sound_to_play = ""


# --- 邏輯控制函式 (已修正 mode 轉換時的 message 覆蓋問題) ---

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
            # --- 處理一輪結束 (修正點在此) ---
            
            is_error_message_present = st.session_state.last_message.startswith("HTML_DIFF_START")
            
            if len(st.session_state.wrong_queue) > 0:
                st.session_state.study_mode = 'REVIEW'
                
                # 🌟 關鍵修正：如果存在詳細錯誤比對訊息，則將模式切換訊息附加到錯誤訊息的前綴部分。
                if is_error_message_present: 
                    
                    # 1. 取得原始錯誤訊息內容 (不含 START/END 標籤)
                    original_content = st.session_state.last_message[len("HTML_DIFF_START"):-len("HTML_DIFF_END")]
                    
                    # 2. 使用明確的分隔符號 |DIFF_SEP| 來分割前綴訊息和 HTML 內容
                    parts = original_content.split('|DIFF_SEP|', 1) 
                    
                    if len(parts) == 2:
                        prefix_message = parts[0]
                        diff_html_content = parts[1] # HTML 內容
                        
                        # 3. 創建新的前綴訊息：將「模式切換」訊息放在最前面
                        new_prefix = f"🔄 一輪結束，進入錯題複習模式！<br><br>{prefix_message.replace('❌ 答錯！', '').replace('⏭️ 跳過！', '')}"
                        
                        # 4. 重新組合並儲存
                        st.session_state.last_message = f"HTML_DIFF_START{new_prefix}|DIFF_SEP|{diff_html_content}HTML_DIFF_END"
                    else:
                        # 錯誤處理：如果無法分割，退回到只顯示模式切換訊息
                        st.session_state.last_message = "🔄 一輪結束，進入錯題複習模式！"
                        
                else:
                    # 如果沒有詳細錯誤比對訊息 (例如，全部答對或沒有作答時結束一輪)
                    st.session_state.last_message = "🔄 一輪結束，進入錯題複習模式！"
                    
                go_next_question() # 遞迴呼叫以設定複習模式的第一題 index                           
            
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
sentence = current_item["sentence"]
sentence_zh = current_item["sentence_zh"]
definition = current_item.get("definition", "N/A")
definition_zh = current_item.get("definition_zh", "N/A") 
# 【新增】取出 blank_index
blank_index = current_item.get("blank_index", -1) 

# 【新增】獲取帶有空白的例句
sentence_with_blank = get_sentence_with_blank(sentence, current_word, blank_index)
# ----------------------------------------


# --- 標題與狀態顯示 ---
st.markdown("<p style='font-size:22px'><b>🎧 單字 + 句子 發音練習</b></p>", unsafe_allow_html=True)

# *** 頁面頂部：集中播放音效 (本地檔案) ***
if st.session_state.local_sound_to_play:
    play_local_audio(st.session_state.local_sound_to_play)
    st.session_state.local_sound_to_play = ""

# *** 頁面頂部：集中播放音效 (gTTS) ***
centralized_gtts_playback()


# 顯示最新的結果訊息
if st.session_state.last_message:
    message = st.session_state.last_message
    
    font_size = "12px" # 調整字體大小
    
    # --- 處理差異化 HTML 顯示 ---
    if message.startswith("HTML_DIFF_START") and message.endswith("HTML_DIFF_END"):
        
        # 提取前綴訊息和 HTML 內容
        content = message[len("HTML_DIFF_START"):-len("HTML_DIFF_END")]
        
        # 使用明確的分隔符號 |DIFF_SEP| 來分割前綴訊息和 HTML 內容
        parts = content.split('|DIFF_SEP|', 1) 
        
        if len(parts) >= 2:
            prefix_message = parts[0]
            diff_html_content = parts[1]
        else:
            prefix_message = content 
            diff_html_content = "" 
        
        # 移除訊息中 Streamlit 內建的圖示，並使用我們自定義的樣式
        display_message = prefix_message.replace("❌ ", "").replace("⏭️ ", "").replace("🔄 ", "")
        
        # 創建完整的 HTML 內容，結合錯誤提示框和差異化顯示
        html_content = f"""
        <div style="background-color: #ffeaea; border-radius: 0.25rem; padding: 1rem; border-left: 0.5rem solid #f00; color: #000;">
            <span style="font-size: {font_size};">{display_message}</span>
            {diff_html_content} 
        </div>
        """
        st.markdown(html_content, unsafe_allow_html=True)
    # --------------------------------------

    elif "答對了" in message or "複習完畢" in message or "全部答對" in message: 
        
        # 移除訊息中 Streamlit 內建的圖示
        display_message = message.replace("✅ ", "").replace("🎉 ", "").replace("💯 ", "")

        html_content = f"""
        <div style="background-color: #e6ffed; border-radius: 0.25rem; padding: 1rem; border-left: 0.5rem solid #090; color: #000;">
            <span style="font-size: {font_size};">✅ {display_message}</span> 
        </div>
        """
        st.markdown(html_content, unsafe_allow_html=True)
        
    elif "答錯" in message or "跳過" in message or "🔄" in message:
        
        # 移除訊息中 Streamlit 內建的圖示
        display_message = message.replace("❌ ", "").replace("⏭️ ", "").replace("🔄 ", "")
        
        html_content = f"""
        <div style="background-color: #ffeaea; border-radius: 0.25rem; padding: 1rem; border-left: 0.5rem solid #f00; color: #000;">
            <span style="font-size: {font_size};">❌ {display_message}</span>
        </div>
        """
        st.markdown(html_content, unsafe_allow_html=True)

    else:
        st.info(message)
    
    # 確保訊息在顯示後被清除
    st.session_state.last_message = ""
        
# --- 狀態模式顯示 ---
if st.session_state.study_mode == 'REVIEW':
    st.warning(f"🔥 錯題複習模式 (剩餘 **{len(st.session_state.wrong_queue)}** 題)")
else:
    display_progress = st.session_state.sequence_cursor 
    if display_progress == total_questions: display_progress = 0
    st.info(f"📖 順序學習模式 (進度 **{display_progress + 1}** / **{total_questions}**)")

# ----------------------------------------------------
# --- 【修正區】發音按鈕區域 (加入圖片) ---
# ----------------------------------------------------
# 步驟 1: 建立欄位佈局 (圖片在左, 按鈕在右)
# [圖片(1), 單字按鈕(2), 例句按鈕(2), 定義按鈕(2)]
col_img, col_btn_word, col_btn_sentence, col_btn_definition = st.columns([1, 2, 2, 2]) 

# 步驟 2: 放置圖片
with col_img:
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # ⚠️ 注意：這裡使用的是與您上傳圖片不同的本地檔案名稱，請確保檔案 Dolingo.jpg 存在。
        image_path = os.path.join(current_dir, "Dolingo.jpg") 
        
        # 顯示圖片 (寬度調整為 70px)
        st.image(image_path, width=70) 
    except Exception as e:
        # 找不到圖片時不顯示任何東西
        pass 

# 步驟 3: 放置按鈕
with col_btn_word:
    if st.button("▶ 單字（英）"):
        set_gtts_to_play(current_word, 'en')
    
with col_btn_sentence:
    # 這裡的按鈕發音還是使用原來的完整句子
    if st.button("▶ 例句（英）"):
        set_gtts_to_play(sentence, 'en')
    
with col_btn_definition: 
    if st.button("▶ 定義（英）"):
        set_gtts_to_play(definition, 'en')


# 【新增/修正】單字呈現方式
st.markdown(f"""
<div style="background-color: #f7f7f7; border-radius: 8px; padding: 15px; margin-bottom: 20px; border: 1px solid #ddd;">
    <p style="font-size: 24px; color: #444; margin-bottom: 5px;">請填空：</p>
    <p style="font-size: 32px; font-weight: bold; color: #1f77b4; line-height: 1.5;">{sentence_with_blank}</p>
</div>
""", unsafe_allow_html=True)


# --- 單字答題表單 ---
input_key = f"input_{current_index}_{st.session_state.study_mode}" 

with st.form(key=f"form_{current_index}", clear_on_submit=True):
    # 【修正】修改提示文字
    user_input = st.text_input(f"請輸入句中的空白單字", key=input_key, autocomplete="off")
    submitted = st.form_submit_button("提交答案 (或按 Enter)")

  
    if submitted:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_text = user_input.strip().lower()
        is_correct = (user_text == current_word.lower())

        # --- 答案處理與狀態更新 ---
        
        if is_correct:
            st.session_state.stats[current_index]["正確"] += 1
            st.session_state.last_message = "✅ 答對了！" 
            if current_index in st.session_state.wrong_queue:
                st.session_state.wrong_queue.remove(current_index) 
            
            # *** 設定正確音效路徑 (本地音效，假設音效檔在 audio 資料夾) ***
            st.session_state.local_sound_to_play = "audio/duolingo_style_correct.mp3" 
            
            # 立即跳下一題 (無延遲)
            go_next_question()

        else:
            st.session_state.stats[current_index]["錯誤"] += 1
            
            # --- 【修改】加入差異化顯示 ---
            # 1. 計算並取得差異 HTML 內容
            diff_html = get_diff_html(current_word, user_text)
            
            # 2. 準備顯示訊息 (將差異 HTML 儲存到 last_message)
            msg_prefix = f"❌ 答錯！正確答案是：**{current_word}** (你的輸入：**{user_text}**)" if user_text else f"⏭️ 跳過！正確答案是：**{current_word}**"
            
            # 🌟 使用明確的分隔符號 |DIFF_SEP| 儲存訊息
            st.session_state.last_message = f"HTML_DIFF_START{msg_prefix}|DIFF_SEP|{diff_html}HTML_DIFF_END"
            # --------------------------------

            if current_index not in st.session_state.wrong_queue:
                st.session_state.wrong_queue.append(current_index) 
            
            if st.session_state.study_mode == 'REVIEW' and current_index in st.session_state.wrong_queue:
                # 答錯或跳過後，將該題移到隊列尾部，避免連續做同一題
                if st.session_state.wrong_queue[0] == current_index:
                    item = st.session_state.wrong_queue.pop(0)
                    st.session_state.wrong_queue.append(item)
            
            # *** 設定錯誤音效路徑 (本地音效，假設音效檔在 audio 資料夾) ***
            st.session_state.local_sound_to_play = "audio/dong_dong.mp3" 

            # 立即跳下一題 (無延遲)
            go_next_question()


        # 紀錄歷史
        st.session_state.history.append({
            "模式": "複習" if st.session_state.study_mode == 'REVIEW' else "一般",
            "題號": current_index + 1,
            "單字": current_word,
            "輸入": user_input,
            "結果": "正確" if is_correct else "錯誤",
            "時間": now_str
        })

        st.rerun() # 重新執行腳本

 # ----------------------------------------------------

st.write(f"中文單字翻譯：**{translation}**")
st.write(f"**中文翻譯：** *{sentence_zh}*") # 將這個移到例句下方
st.markdown(f"**英文定義：** *{definition}*") 
st.write(f"**中文定義：** *{definition_zh}*") 
       

# --- 側邊欄統計 (保持不變) ---
st.sidebar.header("📊 練習進度統計")
st.sidebar.write(f"目前模式：**{st.session_state.study_mode}**")
st.sidebar.write(f"待複習錯題數：**{len(st.session_state.wrong_queue)}**")

st.sidebar.subheader("📈 單字答題統計")
stats_list = []
for i, item in enumerate(word_bank):
    s = st.session_state.stats[i]
    total_try = s["正確"] + s["錯誤"]
    rate = f"{s['正確']}/{total_try}" if total_try > 0 else "0/0"
    
    # --- 狀態燈邏輯 ---
    status_light = "⚪" # 預設: 尚未作答
    
    # 1. 🔴 錯題隊列中 (最高優先級)
    if i in st.session_state.wrong_queue:
        status_light = "🔴" 
    
    # 2. 🟢 已經正確答對過 (至少答對一次，且不在錯題隊列中)
    elif s["正確"] > 0:
        status_light = "🟢" 
    
    # 3. 🟡 曾答錯，待複習 (曾有錯誤記錄，但還沒有正確記錄，且不在隊列中)
    elif s["錯誤"] > 0 and s["正確"] == 0:
        status_light = "🟡" 
        
    stats_list.append({
        "狀態": status_light,
        "題號": i + 1,
        "單字": item["word"],
        "正確率": rate
    })
st.sidebar.dataframe(pd.DataFrame(stats_list), use_container_width=True)

st.sidebar.subheader("📝 歷史紀錄")
if st.session_state.history:
    st.sidebar.dataframe(pd.DataFrame(st.session_state.history[::-1]), use_container_width=True)