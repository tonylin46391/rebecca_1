import streamlit as st
import datetime
import pandas as pd
# 移除 os 函式庫，因為不再讀取本地檔案
# import os 

# 引入 gTTS 來生成語音，以及 io 來處理音訊數據流
from gtts import gTTS
import io


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
     "sentence": "He is an an ace athlete.",
     "sentence_zh": "他是一位一流的運動員。",
     "definition": "Someone described as an ace is extremely good at something.",
     "definition_zh": "被描述為高手的人，在某方面是非常優秀的。"},
     
    {"word": "located", "translation": "位於；坐落於",
     "sentence": "The alligator pond was located near the center of the zoo.",
     "sentence_zh": "鱷魚池位於動物園的中心附近。",
     "definition": "Where something is located is where it is.",
     "definition_zh": "某物被定位（located）的地方就是它所在的位置。"},
]


# 移除所有關於本地音檔路徑和檔案讀取的程式碼

def play_audio_gtts(text: str, lang: str):
    """
    使用 gTTS 生成 MP3 音訊並直接在 Streamlit 中播放。
    音訊內容儲存在 BytesIO 中，不產生實體檔案。
    """
    if not text:
        st.warning("⚠ 播放內容為空，無法生成語音。")
        return
        
    try:
        # 1. 產生 gTTS 物件
        tts = gTTS(text=text, lang=lang)
        
        # 2. 使用 BytesIO 儲存生成的音訊
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        # 3. 在 Streamlit 中播放
        st.audio(fp, format="audio/mp3")
    except Exception as e:
        st.error(f"生成語音時發生錯誤：{e}")


# --- 初始化 Session State ---
total_questions = len(word_bank)
# 確保 hash 包含新的欄位，讓新的 word_bank 會觸發初始化
current_word_hash = hash(tuple((item['word'], item.get('definition_zh')) for item in word_bank))

if "word_bank_hash" not in st.session_state or st.session_state.word_bank_hash != current_word_hash:
    st.session_state.wrong_queue = []
    st.session_state.study_mode = 'LEARNING' 
    st.session_state.sequence_cursor = 0
    st.session_state.current_display_index = 0
    st.session_state.stats = [{"正確": 0, "錯誤": 0} for _ in range(total_questions)]
    st.session_state.history = []
    st.session_state.word_bank_hash = current_word_hash
    st.session_state.last_message = "" # 用於儲存最新的結果訊息
    st.toast("新題庫已載入！")
else:
    # 確保 last_message 存在
    if "last_message" not in st.session_state:
        st.session_state.last_message = ""

# --- 邏輯控制函式 ---

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
        
        # 1. 先將游標推進
        st.session_state.sequence_cursor += 1
        
        # 2. 檢查推進後的游標是否還在範圍內
        if st.session_state.sequence_cursor < total_questions:
            # 3. 顯示新游標所指向的題目
            st.session_state.current_display_index = st.session_state.sequence_cursor
        
        # 4. 游標已到達或超過範圍 (一輪結束)
        else:
            # --- 處理一輪結束 ---
            
            if len(st.session_state.wrong_queue) > 0:
                st.session_state.study_mode = 'REVIEW'
                st.session_state.last_message = "🔄 一輪結束，進入錯題複習模式！"
                # 遞迴呼叫自己，讓它立刻抓取第一題錯題
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
sentence = current_item["sentence"]
sentence_zh = current_item["sentence_zh"]
definition = current_item.get("definition", "N/A")
definition_zh = current_item.get("definition_zh", "N/A") 


# 移除所有關於本地音檔路徑的程式碼

# --- 標題與狀態顯示 ---
st.markdown("<p style='font-size:22px'><b>🎧 單字 + 句子 發音練習</b></p>", unsafe_allow_html=True)

# 顯示最新的結果訊息
if st.session_state.last_message:
    # 判斷訊息類型並用不同顏色顯示
    if "答對了" in st.session_state.last_message or "複習完畢" in st.session_state.last_message or "全部答對" in st.session_state.last_message:
        st.success(st.session_state.last_message)
    elif "答錯" in st.session_state.last_message or "跳過" in st.session_state.last_message:
        # 使用 st.error 模擬您的圖片效果 (帶有紅X)
        st.error(st.session_state.last_message)
    else:
        st.info(st.session_state.last_message)
    
    # 確保訊息在顯示後被清除，避免重複顯示
    st.session_state.last_message = "" 


if st.session_state.study_mode == 'REVIEW':
    st.warning(f"🔥 錯題複習模式 (剩餘 {len(st.session_state.wrong_queue)} 題)")
else:
    display_progress = st.session_state.sequence_cursor 
    if display_progress == total_questions: display_progress = 0
    st.info(f"📖 順序學習模式 (進度 {display_progress + 1} / {total_questions})")

# 更新按鈕標題，包含定義
st.markdown("<p style='font-size:18px'>📌 發音按鈕 (單字 / 英文例句 / 中文翻譯 / 英文定義 / 中文定義)</p>", unsafe_allow_html=True)
st.markdown("<p style='font-size:18px'>✏️ 單字測驗</p>", unsafe_allow_html=True)

# --- 五個發音按鈕 (使用 gTTS 替換 play_audio) ---
col1, col2, col3, col4, col5 = st.columns(5) 
with col1:
    if st.button("▶ 單字（英）"):
        # 呼叫 gTTS 播放單字 (英文 'en')
        play_audio_gtts(current_word, 'en')
with col2:
    if st.button("▶ 例句（英）"):
        # 呼叫 gTTS 播放英文例句 (英文 'en')
        play_audio_gtts(sentence, 'en')
with col3:
    if st.button("▶ 例句（中）"):
        # 呼叫 gTTS 播放中文例句 (中文 'zh-tw')
        play_audio_gtts(sentence_zh, 'zh-tw')
with col4: # 英文定義按鈕
    if st.button("▶ 定義（英）"):
        # 呼叫 gTTS 播放英文定義 (英文 'en')
        play_audio_gtts(definition, 'en')
with col5: # 中文定義按鈕
    if st.button("▶ 定義（中）"):
        # 呼叫 gTTS 播放中文定義 (中文 'zh-tw')
        play_audio_gtts(definition_zh, 'zh-tw')


# 顯示文字
st.write(f"中文單字翻譯：**{translation}**")
st.write(f"英文例句：*{sentence}*")
st.write(f"中文翻譯：*{sentence_zh}*")
st.markdown(f"**英文定義：** *{definition}*") 
st.write(f"中文定義：*{definition_zh}*") 


# --- 單字答題表單 (此處不變) ---
input_key = f"input_{current_index}_{st.session_state.study_mode}" 

with st.form(key=f"form_{current_index}", clear_on_submit=True):
    user_input = st.text_input("請輸入單字 (輸入完按 Enter 即可)", key=input_key, autocomplete="off")
    submitted = st.form_submit_button("提交答案 (或按 Enter)")
    
    if submitted:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_text = user_input.strip().lower()
        is_correct = (user_text == current_word.lower())

        # --- 答案處理與狀態更新 ---
        
        if is_correct:
            st.session_state.stats[current_index]["正確"] += 1
            st.session_state.last_message = "✅ 答對了！" # 儲存正確訊息
            if current_index in st.session_state.wrong_queue:
                st.session_state.wrong_queue.remove(current_index) # 答對後移出錯題隊列
        else:
            st.session_state.stats[current_index]["錯誤"] += 1
            msg = f"❌ 答錯！正確答案是：{current_word}" if user_text else f"⏭️ 跳過！正確答案是：{current_word}"
            st.session_state.last_message = msg # 儲存錯誤訊息
            
            if current_index not in st.session_state.wrong_queue:
                st.session_state.wrong_queue.append(current_index) # 答錯後加入錯題隊列
            
            if st.session_state.study_mode == 'REVIEW' and current_index in st.session_state.wrong_queue:
                if st.session_state.wrong_queue[0] == current_index:
                    item = st.session_state.wrong_queue.pop(0)
                    st.session_state.wrong_queue.append(item)


        # 紀錄歷史
        st.session_state.history.append({
            "模式": "複習" if st.session_state.study_mode == 'REVIEW' else "一般",
            "題號": current_index + 1,
            "單字": current_word,
            "輸入": user_input,
            "結果": "正確" if is_correct else "錯誤",
            "時間": now_str
        })

        go_next_question()
        st.rerun()

# --- 側邊欄統計 (此處不變) ---
st.sidebar.header("📊 練習進度統計")
st.sidebar.write(f"目前模式：**{st.session_state.study_mode}**")
st.sidebar.write(f"待複習錯題數：{len(st.session_state.wrong_queue)}")

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