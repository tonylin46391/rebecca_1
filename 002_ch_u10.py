import streamlit as st
import datetime
import pandas as pd
import os 
from gtts import gTTS
import io
import difflib
import html

# 設定頁面配置,側邊欄初始狀態為展開
st.set_page_config(
    page_title="中文詞彙聽力練習",
    page_icon="🎧",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Duolingo 風格 CSS 樣式 ---
st.markdown("""
<style>
/* 隱藏 Streamlit 預設元素 - 但保留側邊欄控制按鈕 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* 確保側邊欄控制按鈕可見 */
button[kind="header"] {
    visibility: visible !important;
    display: block !important;
}

[data-testid="collapsedControl"] {
    visibility: visible !important;
    display: block !important;
    z-index: 9999 !important;
}

/* 隱藏音訊播放器 */
audio {
    display: none !important;
}

.stAudio {
    display: none !important;
}

/* 頁面背景色 */
.stApp {
    background-color: #F7F7F7;
}

/* 主要卡片樣式 */
.main-card {
    background: white;
    border-radius: 16px;
    padding: 32px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin: 20px 0;
}

/* 標題樣式 */
.title-text {
    font-size: 100px;
    font-weight: 700;
    color: #1CB0F6;
    text-align: left;
    margin-bottom: 24px;
}

/* Duolingo 綠色按鈕樣式 */
div.stButton > button {
    width: 100%;
    background-color: #58CC02 !important;
    color: white !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 16px 24px !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 0 #58A700 !important;
    transition: all 0.1s ease !important;
    cursor: pointer !important;
}

div.stButton > button:hover {
    background-color: #61E002 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 0 #58A700 !important;
}

div.stButton > button:active {
    background-color: #58A700 !important;
    transform: translateY(2px) !important;
    box-shadow: 0 2px 0 #58A700 !important;
}

/* 提交按鈕樣式 */
.stForm button[kind="primary"] {
    display: none !important;
}

/* 輸入框樣式 */
.stTextInput > div > div > input {
    border: 2px solid #E5E5E5 !important;
    border-radius: 12px !important;
    padding: 16px !important;
    font-size: 18px !important;
    transition: all 0.2s ease !important;
}

.stTextInput > div > div > input:focus {
    border-color: #1CB0F6 !important;
    box-shadow: 0 0 0 3px rgba(28, 176, 246, 0.1) !important;
}

.stTextInput > label {
    font-size: 16px !important;
    font-weight: 600 !important;
    color: #3C3C3C !important;
    margin-bottom: 8px !important;
}

/* 成功訊息樣式 */
.success-message {
    background: linear-gradient(135deg, #58CC02 0%, #61E002 100%);
    color: white;
    padding: 20px;
    border-radius: 16px;
    font-size: 20px;
    font-weight: 700;
    text-align: left;
    margin: 20px 0;
    box-shadow: 0 4px 12px rgba(88, 204, 2, 0.3);
}

/* 錯誤訊息樣式 */
.error-message {
    background: transparent;
    color: #3C3C3C;
    padding: 10px;
    border-radius: 0px;
    font-size: 16px;
    font-weight: 700;
    text-align: left;
    margin: 10px 0;
    box-shadow: none;
}

/* 資訊訊息樣式 */
.info-message {
    background: linear-gradient(135deg, #1CB0F6 0%, #4DC3FF 100%);
    color: white;
    padding: 20px;
    border-radius: 16px;
    font-size: 18px;
    font-weight: 700;
    text-align: left;
    margin: 20px 0;
    box-shadow: 0 4px 12px rgba(28, 176, 246, 0.3);
}

/* 警告訊息樣式 */
.warning-message {
    background: linear-gradient(135deg, #FF9600 0%, #FFB800 100%);
    color: white;
    padding: 16px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    margin: 16px 0;
    box-shadow: 0 4px 12px rgba(255, 150, 0, 0.3);
}

/* 進度條樣式 */
.progress-bar {
    width: 100%;
    height: 16px;
    background-color: #E5E5E5;
    border-radius: 8px;
    overflow: hidden;
    margin: 20px 0;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #58CC02 0%, #61E002 100%);
    transition: width 0.3s ease;
}

/* 側邊欄樣式 */
[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E5E5E5;
}

[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3 {
    color: #1CB0F6 !important;
}

/* 貓頭鷹圖片樣式 */
.owl-image {
    animation: bounce 2s infinite;
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

/* 詞彙顯示區域 */
.word-display {
    background: linear-gradient(135deg, #FFC800 0%, #FFD700 100%);
    color: white;
    font-size: 48px;
    font-weight: 900;
    text-align: center;
    padding: 40px;
    border-radius: 20px;
    margin: 30px 0;
    box-shadow: 0 8px 16px rgba(255, 200, 0, 0.3);
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

/* 統計卡片 */
.stat-card {
    background: white;
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    border-left: 4px solid #58CC02;
}

</style>
""", unsafe_allow_html=True)

# JavaScript 用於自動聚焦
st.markdown("""
<script>
// 自動聚焦到輸入框
function focusInput() {
    const input = window.parent.document.querySelector('input[type="text"]');
    if (input && document.activeElement !== input) {
        input.focus();
    }
}

// 頁面載入時聚焦
window.addEventListener('load', function() {
    setTimeout(focusInput, 100);
});

// 監聽頁面變化,持續保持聚焦
const observer = new MutationObserver(focusInput);
observer.observe(document.body, {
    childList: true,
    subtree: true
});

// 每隔100ms檢查一次聚焦狀態
setInterval(focusInput, 100);

// 監聽所有可能導致失焦的事件
document.addEventListener('click', function(e) {
    if (e.target.tagName !== 'INPUT') {
        setTimeout(focusInput, 10);
    }
});

// 監聽鍵盤事件,確保輸入時保持聚焦
document.addEventListener('keydown', function() {
    setTimeout(focusInput, 10);
});
</script>
""", unsafe_allow_html=True)

# 詞彙列表
chinese_words = [ 
    "冷風", "雪梨", "港口", "卻是", "冬天",
    "台灣", "季節", "相反", "煙火", "點心",
    "等待", "綻放", "夜空", "照片", "分享",
    "雖然", "喜歡", "春節", "年貨", "期待", "年夜飯"
]

word_bank = []
for word in chinese_words:
    word_item = {
        "word": word,
        "translation": word,
    }
    word_bank.append(word_item)


def play_local_audio(filename: str):
    """播放本地音效檔案"""
    try:
        audio_bytes = open(filename, 'rb').read()
        placeholder = st.empty()
        with placeholder:
            st.audio(audio_bytes, format='audio/mp3', autoplay=True)
    except FileNotFoundError:
        st.warning(f"⚠ 找不到音效檔案:'{filename}'")
    except Exception as e:
        st.error(f"播放音效時發生錯誤:{e}")


def set_gtts_to_play(text: str, lang: str):
    """設定要播放的 TTS 文字"""
    if text:
        st.session_state.gtts_to_play = (text, lang)
        st.rerun()
    else:
        st.warning("⚠ 播放內容為空")
        

def centralized_gtts_playback():
    """集中處理 gTTS 音訊播放"""
    if st.session_state.gtts_to_play is not None:
        text, lang = st.session_state.gtts_to_play
        st.session_state.gtts_to_play = None
        
        placeholder = st.empty() 
        
        try:
            tts = gTTS(text=text, lang=lang)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            
            with placeholder:
                st.audio(fp, format="audio/mp3", autoplay=True)
            
        except Exception as e:
            st.error(f"生成語音時發生錯誤:{e}")


def get_diff_html(a: str, b: str) -> str:
    """生成差異化顯示的 HTML(中文版本)"""
    s = difflib.SequenceMatcher(None, a, b)

    correct = []
    inputed = []

    GREEN = "background:#58CC02;color:white;"
    RED = "background:#FF4B4B;color:white;"
    EMPTY = "background:#E5E5E5;color:white;"

    def span(text, style):
        text = html.escape(text)
        return f"<span style='{style}display:inline-block;width:35px;height:45px;line-height:45px;margin:2px;border-radius:8px;font-family:Arial, sans-serif;text-align:center;font-size:27px;font-weight:600;'>{text}</span>"

    for opcode, a1, a2, b1, b2 in s.get_opcodes():
        A = a[a1:a2]
        B = b[b1:b2]

        if opcode == "equal":
            for x, y in zip(A, B):
                correct.append(span(x, GREEN))
                inputed.append(span(y, GREEN))

        elif opcode == "replace":
            L = max(len(A), len(B))
            for i in range(L):
                ca = A[i] if i < len(A) else "_"
                cb = B[i] if i < len(B) else "_"
                correct.append(span(ca, RED))
                inputed.append(span(cb, RED))

        elif opcode == "delete":
            for ch in A:
                correct.append(span(ch, RED))
                inputed.append(span("_", EMPTY))

        elif opcode == "insert":
            for ch in B:
                correct.append(span("_", EMPTY))
                inputed.append(span(ch, RED))

    return f"""<div style='text-align:left;margin-top:10px;margin-bottom:10px;'>
        <div style='margin-bottom:5px;'>{''.join(correct)}</div>
        <div style='font-size:15px;margin:5px;color:#666;'>⬇️</div>
        <div>{''.join(inputed)}</div>
    </div>"""


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
    st.toast("🎉 新題庫已載入!")
else:
    if "last_message" not in st.session_state:
        st.session_state.last_message = ""
    if "gtts_to_play" not in st.session_state:
        st.session_state.gtts_to_play = None
    if "local_sound_to_play" not in st.session_state:
        st.session_state.local_sound_to_play = ""


def go_next_question():
    """進入下一題"""
    if st.session_state.study_mode == 'REVIEW':
        if len(st.session_state.wrong_queue) > 0:
            next_idx = st.session_state.wrong_queue[0]
            st.session_state.current_display_index = next_idx
        else:
            st.session_state.study_mode = 'LEARNING'
            st.session_state.sequence_cursor = 0
            st.session_state.last_message = "🎉 錯題複習完畢!開始新的一輪!"
            st.session_state.current_display_index = 0
    
    elif st.session_state.study_mode == 'LEARNING':
        st.session_state.sequence_cursor += 1
        
        if st.session_state.sequence_cursor < total_questions:
            st.session_state.current_display_index = st.session_state.sequence_cursor
        else:
            if len(st.session_state.wrong_queue) > 0:
                st.session_state.study_mode = 'REVIEW'
                st.session_state.last_message = "🔄 一輪結束,進入錯題複習模式!"
                go_next_question()
            else:
                st.session_state.sequence_cursor = 0
                st.session_state.current_display_index = 0
                st.session_state.last_message = "💯 太強了!全部答對,直接開始新的一輪!"


# --- 主介面 ---
current_index = st.session_state.current_display_index
current_item = word_bank[current_index]
current_word = current_item["word"]
translation = current_item["translation"]

# 頁面標題
st.markdown('<p class="title-text">🎧 中文詞彙聽力練習</p>', unsafe_allow_html=True)

# 播放音效
if st.session_state.local_sound_to_play:
    play_local_audio(st.session_state.local_sound_to_play)
    st.session_state.local_sound_to_play = ""

centralized_gtts_playback()

# 顯示訊息
if st.session_state.last_message:
    message = st.session_state.last_message
    
    # 檢查是否有差異化顯示
    if message.startswith("HTML_DIFF_START") and message.endswith("HTML_DIFF_END"):
        content = message[len("HTML_DIFF_START"):-len("HTML_DIFF_END")]
        parts = content.split('|DIFF_SEP|', 1)
        
        if len(parts) >= 2:
            prefix_message = parts[0]
            diff_html_content = parts[1]
        else:
            prefix_message = content
            diff_html_content = ""
        
        display_message = prefix_message.replace("❌ ", "").replace("⭐️ ", "").replace("🔄 ", "")
        
        st.markdown(f"""
        <div class="error-message">
            {display_message}
            {diff_html_content}
        </div>
        """, unsafe_allow_html=True)
    
    else:
        is_correct_msg = "答對了" in message or "複習完畢" in message or "全部答對" in message
        is_wrong_msg = "答錯" in message or "跳過" in message or "🔄" in message
        
        if is_correct_msg: 
            display_message = message.replace("✅ ", "").replace("🎉 ", "").replace("💯 ", "")
            st.markdown(f'<div class="success-message">✅ {display_message}</div>', unsafe_allow_html=True)
            
        elif is_wrong_msg:
            display_message = message.replace("❌ ", "").replace("⭐️ ", "").replace("🔄 ", "")
            st.markdown(f'<div class="error-message">❌ {display_message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="info-message">{message}</div>', unsafe_allow_html=True)
    
    st.session_state.last_message = ""

# 顯示模式和進度
if st.session_state.study_mode == 'REVIEW':
    st.markdown(f'<div class="warning-message">🔥 錯題複習模式 (剩餘 {len(st.session_state.wrong_queue)} 題)</div>', unsafe_allow_html=True)

# 貓頭鷹圖片和播放按鈕
col_img, col_btn = st.columns([1, 8])

with col_img:
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "Dolingo.jpg")
        st.markdown("""
        <div style="display: flex; align-items: center; height: 100%;">
            <div class="owl-image">
        """, unsafe_allow_html=True)
        st.image(image_path, width=60)
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)
    except:
        st.markdown("🦉", unsafe_allow_html=True)

with col_btn:
    st.markdown('<div style="padding-top: 0px;">', unsafe_allow_html=True)
    if st.button("🔊 播放詞彙發音"): 
        set_gtts_to_play(current_word, 'zh-tw')
    st.markdown('</div>', unsafe_allow_html=True)

# 詞彙顯示(答對後顯示)
if st.session_state.last_message and "答對" in st.session_state.last_message:
    st.markdown(f'<div class="word-display">{current_word}</div>', unsafe_allow_html=True)

# 答題表單
input_key = f"input_{current_index}_{st.session_state.study_mode}" 

with st.form(key=f"form_{current_index}", clear_on_submit=True):
    user_input = st.text_input("✏️ 請輸入你聽到的中文詞彙", key=input_key, autocomplete="off", placeholder="在此輸入...")
    submitted = st.form_submit_button("提交")
    
    if submitted:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_text = user_input.strip()
        is_correct = (user_text == current_word) 

        if is_correct:
            st.session_state.stats[current_index]["正確"] += 1
            
            # 生成差異化顯示(答對時也顯示)
            diff_html = get_diff_html(current_word, user_text)
            st.session_state.last_message = f"HTML_DIFF_START✅ 答對了!太棒了!|DIFF_SEP|{diff_html}HTML_DIFF_END"
            
            if current_index in st.session_state.wrong_queue:
                st.session_state.wrong_queue.remove(current_index) 
            
            st.session_state.local_sound_to_play = "audio/duolingo_style_correct.mp3" 
            go_next_question()

        else:
            st.session_state.stats[current_index]["錯誤"] += 1
            
            # 生成差異化顯示
            diff_html = get_diff_html(current_word, user_text)
            msg_prefix = f"❌ 答錯了!正確答案是:{current_word}" if user_text else f"⭐️ 跳過!正確答案是:{current_word}"
            st.session_state.last_message = f"HTML_DIFF_START{msg_prefix}|DIFF_SEP|{diff_html}HTML_DIFF_END"
            
            if current_index not in st.session_state.wrong_queue:
                st.session_state.wrong_queue.append(current_index) 
            
            if st.session_state.study_mode == 'REVIEW' and current_index in st.session_state.wrong_queue:
                if st.session_state.wrong_queue[0] == current_index:
                    item = st.session_state.wrong_queue.pop(0)
                    st.session_state.wrong_queue.append(item)
            
            st.session_state.local_sound_to_play = "audio/dong_dong.mp3" 
            go_next_question()

        st.session_state.history.append({
            "模式": "複習" if st.session_state.study_mode == 'REVIEW' else "一般",
            "題號": current_index + 1,
            "詞彙": current_word,
            "輸入": user_input,
            "結果": "正確" if is_correct else "錯誤",
            "時間": now_str
        })

        st.rerun()

# --- 側邊欄統計 ---
with st.sidebar:
    st.markdown("## 📊 學習統計")
    
    st.markdown(f"""
    <div class="stat-card">
        <strong>學習模式:</strong> {st.session_state.study_mode}<br>
        <strong>待複習題數:</strong> {len(st.session_state.wrong_queue)}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📈 詞彙統計")
    stats_list = []
    for i, item in enumerate(word_bank):
        s = st.session_state.stats[i]
        total_try = s["正確"] + s["錯誤"]
        rate = f"{s['正確']}/{total_try}" if total_try > 0 else "0/0"
        
        status_light = "⚪"
        if i in st.session_state.wrong_queue:
            status_light = "🔴" 
        elif s["正確"] > 0:
            status_light = "🟢" 
        elif s["錯誤"] > 0:
            status_light = "🟡" 
            
        stats_list.append({
            "狀態": status_light,
            "題號": i + 1,
            "詞彙": item["word"],
            "正確率": rate
        })
    st.dataframe(pd.DataFrame(stats_list), use_container_width=True, hide_index=True)

    st.markdown("### 📝 歷史紀錄")
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history[::-1]), use_container_width=True, hide_index=True)