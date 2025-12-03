import streamlit as st
import datetime
import pandas as pd
import os # 用來讀取本地 mp3 檔案
import random # 【新增】用於隨機化測驗類型和多選選項


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
     # 【修正】移除原單字中句子的 typo "an an"
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


# 預先下載的 mp3 放在這個資料夾
AUDIO_DIR = "audio"

def play_audio(filepath: str):
    """播放本地 mp3，如果檔案不存在就提示警告。"""
    if not os.path.exists(filepath):
        st.warning(f"⚠ 找不到音檔：{os.path.basename(filepath)}")
        st.caption(f"請確保您的音檔檔名符合格式，例如：{os.path.basename(filepath)}")
        return
    try:
        with open(filepath, "rb") as f:
            audio_bytes = f.read()
        st.audio(audio_bytes, format="audio/mp3")
    except Exception as e:
        st.error(f"讀取音檔時發生錯誤：{e}")

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
    st.session_state.last_message = ""
    st.session_state.quiz_type = 'TRANSLATION' # 【新增】記錄當前測驗類型
    st.toast("新題庫已載入！")
else:
    if "last_message" not in st.session_state:
        st.session_state.last_message = ""
    if "quiz_type" not in st.session_state:
         st.session_state.quiz_type = 'TRANSLATION'

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

# --- 測驗產生器 ---

def generate_mc_quiz(current_item, all_words, question_type):
    """根據當前單字和類型，產生問題、正確答案和選項。"""
    
    correct_word = current_item["word"]
    
    # 1. 決定問題提示 (Prompt)
    if question_type == 'TRANSLATION':
        # 範例：翻譯這個單字：代辦處；經銷處；政府機構
        prompt = f"翻譯這個單字：\n\n**{current_item['translation']}**"
        audio_path_key = 'word_en'
    elif question_type == 'DEFINITION':
        # 範例：哪個單字符合這個定義：如果你在一家代辦處工作...
        prompt = f"哪個單字符合這個定義：\n\n**{current_item['definition_zh']}**"
        audio_path_key = 'def_zh'
    else: 
        # 預設為 TRANSLATION
        prompt = f"翻譯這個單字：\n\n**{current_item['translation']}**"
        audio_path_key = 'word_en'

    # 2. 產生選項 (Choices)
    all_other_words = [w for w in all_words if w != correct_word]
    num_choices = 4
    num_distractors = num_choices - 1

    # 確保有足夠的干擾項
    if len(all_other_words) >= num_distractors:
        distractors = random.sample(all_other_words, num_distractors)
    else:
        # 如果題庫太小，就重複使用或隨機挑選
        temp_list = all_other_words * 2
        distractors = random.sample(temp_list, num_distractors)

    choices = [correct_word] + distractors
    random.shuffle(choices)
    
    return prompt, correct_word, choices, audio_path_key

# --- 答案檢查器 (取代舊的表單提交邏輯) ---
def check_answer_and_proceed(user_choice):
    """處理使用者點擊按鈕後的邏輯：檢查答案、更新統計、跳到下一題。"""
    
    current_index = st.session_state.current_display_index
    current_word = word_bank[current_index]["word"]
    is_correct = (user_choice.lower() == current_word.lower())
    
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. 更新統計與訊息
    if is_correct:
        st.session_state.stats[current_index]["正確"] += 1
        st.session_state.last_message = "✅ 答對了！" 
        if current_index in st.session_state.wrong_queue:
            st.session_state.wrong_queue.remove(current_index)
        
    else:
        st.session_state.stats[current_index]["錯誤"] += 1
        st.session_state.last_message = f"❌ 答錯！正確答案是：{current_word}"
        if current_index not in st.session_state.wrong_queue:
            st.session_state.wrong_queue.append(current_index)
        
        # 複習模式下，答錯的題目要保持在隊列中
        if st.session_state.study_mode == 'REVIEW' and current_index in st.session_state.wrong_queue:
            if st.session_state.wrong_queue[0] == current_index:
                item = st.session_state.wrong_queue.pop(0)
                st.session_state.wrong_queue.append(item)


    # 2. 紀錄歷史
    st.session_state.history.append({
        "模式": "複習" if st.session_state.study_mode == 'REVIEW' else "一般",
        "題型": st.session_state.quiz_type,
        "題號": current_index + 1,
        "單字": current_word,
        "輸入": user_choice,
        "結果": "正確" if is_correct else "錯誤",
        "時間": now_str
    })
    
    # 3. 準備下一題
    go_next_question()
    
    # 隨機選擇下一個測驗類型，增加多樣性
    st.session_state.quiz_type = random.choice(['TRANSLATION', 'DEFINITION'])
    st.rerun()


# --- 介面顯示：Duolingo Style 主挑戰區 ---

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


# 組合音檔路徑
base_name = f"{current_index + 1:02d}_{current_word}"
word_audio_path     = os.path.join(AUDIO_DIR, f"{base_name}_word_en.mp3")
sent_en_audio_path = os.path.join(AUDIO_DIR, f"{base_name}_sent_en.mp3")
sent_zh_audio_path = os.path.join(AUDIO_DIR, f"{base_name}_sent_zh.mp3")
def_en_audio_path  = os.path.join(AUDIO_DIR, f"{base_name}_def_en.mp3")
def_zh_audio_path  = os.path.join(AUDIO_DIR, f"{base_name}_def_zh.mp3")

audio_paths = {
    'word_en': word_audio_path,
    'def_zh': def_zh_audio_path
}


# --- 標題與狀態顯示 ---
st.markdown("<p style='font-size:22px'><b>🧠 Duolingo 風格單字測驗</b></p>", unsafe_allow_html=True)

# 顯示最新的結果訊息
if st.session_state.last_message:
    if "答對了" in st.session_state.last_message or "複習完畢" in st.session_state.last_message or "全部答對" in st.session_state.last_message:
        st.success(st.session_state.last_message)
    elif "答錯" in st.session_state.last_message or "跳過" in st.session_state.last_message:
        st.error(st.session_state.last_message)
    else:
        st.info(st.session_state.last_message)
    
    st.session_state.last_message = "" 


if st.session_state.study_mode == 'REVIEW':
    st.warning(f"🔥 錯題複習模式 (剩餘 {len(st.session_state.wrong_queue)} 題)")
else:
    display_progress = st.session_state.sequence_cursor 
    if display_progress == total_questions: display_progress = 0
    st.info(f"📖 順序學習模式 (進度 {display_progress + 1} / {total_questions})")


# --- Duolingo-Style 挑戰區 ---

# 1. 產生當前問題
all_words_list = [item['word'] for item in word_bank]
prompt, correct_word, choices, audio_path_key = generate_mc_quiz(
    current_item, 
    all_words_list, 
    st.session_state.quiz_type
)

# 2. 顯示問題
st.markdown("---")
st.markdown(f"## {prompt}")
st.markdown("---")

# 3. 顯示音頻按鈕
audio_to_play = audio_paths.get(audio_path_key)
if audio_to_play:
    st.caption("🔊 點擊音符聆聽發音 (輔助)")
    if st.button("▶ 聽發音"):
        play_audio(audio_to_play)

st.markdown("### 點擊正確的英文單字:")

# 4. 顯示多選選項 (Tiles)
# 分成兩排顯示
num_choices = len(choices)
midpoint = (num_choices + 1) // 2

cols1 = st.columns(midpoint)
cols2 = st.columns(num_choices - midpoint)

for i in range(num_choices):
    choice = choices[i]
    col = cols1[i] if i < midpoint else cols2[i - midpoint]
    
    with col:
        # 使用 lambda 呼叫答案檢查器
        if st.button(choice, key=f"choice_{i}_{current_index}_{st.session_state.study_mode}_{st.session_state.quiz_type}", use_container_width=True):
            check_answer_and_proceed(choice)


# --- 單字資訊區 (輔助參考/作弊區) ---
st.markdown("---")
st.markdown("### 📚 單字資訊 (點擊這裡可以參考)")

st.write(f"中文單字翻譯：**{translation}**")
st.markdown(f"**英文定義：** *{definition}*") 
st.write(f"中文定義：*{definition_zh}*") 
st.write(f"英文例句：*{sentence}*")
st.write(f"中文翻譯：*{sentence_zh}*")


st.markdown("---")
# 【舊的發音按鈕改為輔助按鈕】
st.caption("發音輔助區 (測試所有音檔)")
col1, col2, col3, col4, col5 = st.columns(5) 
with col1:
    if st.button("單字（英）", key="aux_word"):
        play_audio(word_audio_path)
with col2:
    if st.button("例句（英）", key="aux_sent_en"):
        play_audio(sent_en_audio_path)
with col3:
    if st.button("例句（中）", key="aux_sent_zh"):
        play_audio(sent_zh_audio_path)
with col4: 
    if st.button("定義（英）", key="aux_def_en"):
        play_audio(def_en_audio_path)
with col5: 
    if st.button("定義（中）", key="aux_def_zh"):
        play_audio(def_zh_audio_path)


# --- 側邊欄統計 (保持不變) ---
st.sidebar.header("📊 練習進度統計")
st.sidebar.write(f"目前模式：**{st.session_state.study_mode}**")
st.sidebar.write(f"待複習錯題數：{len(st.session_state.wrong_queue)}")
st.sidebar.write(f"目前題型：**{st.session_state.quiz_type}**")


st.sidebar.subheader("📈 單字答題統計")
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
        "單字": item["word"],
        "正確率": rate
    })
st.sidebar.dataframe(pd.DataFrame(stats_list), use_container_width=True)

st.sidebar.subheader("📝 歷史紀錄")
if st.session_state.history:
    st.sidebar.dataframe(pd.DataFrame(st.session_state.history[::-1]), use_container_width=True)