import streamlit as st
import os
import datetime
import pandas as pd
from gtts import gTTS
from io import BytesIO # 用於處理音訊的記憶體串流

# 故事全文 (用於音檔和完整參考)
STORY_FULL = "聰明的小熊。有一天,口渴的烏鴉為了要喝瓶子裡的水,想出一個喝到水的好方法。森林裡的動物們知道了,都說烏鴉真是聰明!有一次,小熊到外地旅行。到了中午,他又熱又渴,想要找水喝。東找西找,他看到一個裝有半瓶水的小瓶子。小熊馬上找了許多小石頭放進瓶子裡,開心地看著瓶裡的水越升越高。路過的小馬看見小熊的動作,好奇的問:「你為什麼要這麼做呢?」小熊說:「難道你忘了鳥鴉喝水的故事?那鳥鴉多聰明啊!看!我可是一學就會呢!」哈哈哈!」小馬笑著問:「你真聰明」!但是,你為什麼不拿起瓶子喝水呢?」"

# 錯別字題庫（每個元素是一道題目）
# 結構: (正確字, 錯字, 正確句子/段落, 顯示給學生的錯字版本, 提示字詞)
QUIZ_WORDS = [
    ("烏鴉", "鳥鴉", "難道你忘了烏鴉喝水的故事?", "難道你忘了鳥鴉喝水的故事?", "烏鴉 (鳥鴉)"), 
    ("喝到", "喝", "想出一個喝到水的好方法。", "想出一個喝水的好方法。", "喝到 (喝)"), 
    ("瓶子", "瓶", "為了要喝瓶子裡的水。", "為了要喝瓶裡的水。", "瓶子 (瓶)"), 
    ("聰明", "聰名", "都說烏鴉真是聰明!", "都說烏鴉真是聰名!", "聰明 (聰名)"), 
    ("旅行", "旅型", "小熊到外地旅行。", "小熊到外地旅型。", "旅行 (旅型)"), 
    ("找水喝", "找水喝", "想要找水喝。", "想要找水", "找水喝 (找水)"), 
    ("動作", "動做", "路過的小馬看見小熊的動作", "路過的小馬看見小熊的動做", "動作 (動做)"), 
    ("哈哈哈", "哈哈", "哈哈哈!」小馬笑著問", "哈哈!」小馬笑著問", "哈哈哈 (哈哈)") 
]


# 🚨 移除 AUDIO_DIR 設定

# --- 初始化 Session State ---
current_quiz_hash = hash(tuple(item[0] + item[1] for item in QUIZ_WORDS))

if "quiz_hash" not in st.session_state or st.session_state.quiz_hash != current_quiz_hash:
    st.session_state.index = 0
    st.session_state.mode = "normal"
    st.session_state.retry_queue = []
    st.session_state.answered = {}
    st.session_state.history = []
    st.session_state.stats = {item[4]: {"正確": 0, "錯誤": 0} for item in QUIZ_WORDS}
    st.session_state.last_result = "🎉 載入新的錯別字測驗！使用 gTTS 自動發音！"
    st.session_state.played = False
    st.session_state.last_word = None
    st.session_state.quiz_hash = current_quiz_hash
else:
    for item in QUIZ_WORDS:
        if item[4] not in st.session_state.stats:
            st.session_state.stats[item[4]] = {"正確": 0, "錯誤": 0}


# ✅ 播放音訊的函式 (使用 gTTS)
def play_preloaded_audio(text_to_speak: str) -> bool:
    """
    使用 gTTS 將文字轉換為音訊並播放。
    """
    text_to_speak = text_to_speak.strip()
    if not text_to_speak:
        st.warning("沒有可以發音的文字。")
        return False
    
    try:
        # 建立 gTTS 物件，使用中文 (lang='zh-tw' 或 'zh-cn')
        tts = gTTS(text=text_to_speak, lang='zh-tw')
        
        # 使用 BytesIO 存儲音訊資料，而不是寫入本地檔案
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        # Streamlit 播放音訊
        st.audio(audio_fp.read(), format="audio/mp3")
        return True
        
    except Exception as e:
        # gTTS 需要網路連線
        st.error(f"🌐 gTTS 轉換音訊時發生錯誤，請檢查網路連線：{e}")
        return False


# 📌 取得下一個題目
def get_next_word():
    # 獲取題目的輔助函式，返回整個題目元組
    
    # 優先處理錯題 queue (queue 裡存的是 QUIZ_WORDS 的索引值 index)
    if st.session_state.mode == "review":
        if st.session_state.retry_queue:
            return QUIZ_WORDS[st.session_state.retry_queue[0]]
        else:
            st.session_state.mode = "normal"
            st.session_state.index = 0
            st.session_state.last_result = "🎉 錯題複習完成！開始新一輪！"
            return QUIZ_WORDS[st.session_state.index]

    # normal 模式 → 按順序走題庫
    if st.session_state.index < len(QUIZ_WORDS):
        return QUIZ_WORDS[st.session_state.index]
    else:
        # 一輪結束 → 準備錯題複習
        wrongs_indices = [idx for idx, ans in st.session_state.answered.items() if ans is False]
        
        if wrongs_indices:
            st.session_state.mode = "review"
            st.session_state.retry_queue = wrongs_indices.copy()
            st.session_state.last_result = "🔁 進入錯題複習！"
            return QUIZ_WORDS[st.session_state.retry_queue[0]]
        else:
            # 全部答對 → 新一輪
            st.session_state.index = 0
            st.session_state.answered = {} 
            st.session_state.last_result = "🎉 全部正確！開始新一輪！"
            return QUIZ_WORDS[st.session_state.index]


# 提交答案
def submit_answer():
    # 取得當前題目 (使用索引，因為在 callback 中，index 還沒更新)
    current_index = st.session_state.index if st.session_state.mode == "normal" else st.session_state.retry_queue[0]
    
    # 獲取正確答案：QUIZ_WORDS[i][0]
    correct_answer = QUIZ_WORDS[current_index][0] 
    
    # 獲取題目標籤 (用於統計): QUIZ_WORDS[i][4]
    quiz_tag = QUIZ_WORDS[current_index][4] 
    
    # 這裡必須重新獲取 input_key，以確保它是正確的。
    # 為了在 callback 中正確獲取 key，我們可以將其存入 session state。
    # 但更簡單的方式是直接使用最新的 current_index 來重構 key。
    temp_input_key = f"input_{current_index}_{st.session_state.mode}"
    user_input = st.session_state[temp_input_key]
    
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 判斷答案
    is_correct = user_input.strip() == correct_answer

    if is_correct:
        st.session_state.stats[quiz_tag]["正確"] += 1
        result = "正確"
        st.session_state.last_result = f"✅ 答對了！{QUIZ_WORDS[current_index][2]}"

        if st.session_state.mode == "review":
            if current_index in st.session_state.retry_queue:
                st.session_state.retry_queue.remove(current_index)
        else:
            st.session_state.answered[current_index] = True
            
    else:
        st.session_state.stats[quiz_tag]["錯誤"] += 1
        result = "錯誤"
        st.session_state.last_result = f"❌ 答錯！正確答案是：**{correct_answer}** (在句中應為：{QUIZ_WORDS[current_index][2]})"

        if st.session_state.mode == "review":
            st.session_state.retry_queue.remove(current_index)
            st.session_state.retry_queue.append(current_index)
        else:
            st.session_state.answered[current_index] = False
            
    # 紀錄歷史
    st.session_state.history.append({
        "題目 (錯字句)": QUIZ_WORDS[current_index][3],
        "正確答案": correct_answer,
        "結果": result,
        "學生輸入的答案": user_input,
        "時間": now_str
    })

    # normal 模式 → 下一題
    if st.session_state.mode == "normal":
        st.session_state.index += 1

    # 重設播放狀態
    st.session_state.played = False 
    st.session_state.last_word = None
    
    st.rerun() 

# --- 頁面主程式碼執行區塊 ---

st.markdown('<p style="font-size:26px">📜 課文錯別字辨識 (gTTS 線上發音)</p>', unsafe_allow_html=True)

# 取得目前題目
current_quiz_tuple = get_next_word()
correct_word, wrong_word, correct_sentence, wrong_sentence, quiz_tag = current_quiz_tuple
current_index = st.session_state.index if st.session_state.mode == "normal" else st.session_state.retry_queue[0]
input_key = f"input_{current_index}_{st.session_state.mode}" # 確保 key 與 form 中的 key 一致


# 🔊 顯示故事與自動播放音訊
st.subheader("📚 故事內容")
st.markdown(f"**請找出並修正句子中的錯誤：**")
st.markdown(f'<p style="font-size:20px; color: red;">{wrong_sentence}</p>', unsafe_allow_html=True)

# 播放音訊：使用正確句子進行 gTTS 發音
if not st.session_state.played: 
    ok = play_preloaded_audio(correct_sentence) # 使用正確句子發音
    st.session_state.played = ok      
    st.session_state.last_word = correct_sentence if ok else None 

# 顯示最新答題結果訊息
if st.session_state.last_result:
    st.info(st.session_state.last_result)


# 輸入表單
with st.form(key=f"form_{current_index}", clear_on_submit=True): 
    # 讓學生輸入正確的「字/詞」
    st.text_input(f"請輸入句中【{wrong_word}】的正確寫法（正確字/詞）：",
                   key=input_key,
                   autocomplete="off")
    st.form_submit_button("提交答案 (或按 Enter)", on_click=submit_answer)

# 側邊欄進度
st.sidebar.header("📊 學習進度")
total = len(QUIZ_WORDS)
done_indices = [idx for idx, ans in st.session_state.answered.items() if ans is True]
st.sidebar.write(f"✅ 已正確答對題數：{len(done_indices)} / {total}")
st.sidebar.write(f"🔄 待複習錯題數：{len(st.session_state.retry_queue)}")
st.sidebar.write(f"模式：**{st.session_state.mode.upper()}**")

# 答題歷史
st.sidebar.header("📝 答題歷史")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history[::-1])
    st.sidebar.dataframe(df, use_container_width=True)

# 統計 + 狀態燈
st.sidebar.header("📊 錯題統計")
stats_list = []
for item in QUIZ_WORDS:
    tag = item[4]
    s = st.session_state.stats.get(tag, {"正確": 0, "錯誤": 0})
    total_attempts = s["正確"] + s["錯誤"]
    rate = f"{s['正確']}/{total_attempts}" if total_attempts > 0 else "0/0"
    
    # 狀態燈邏輯：現在是基於題目的索引值
    item_index = QUIZ_WORDS.index(item)
    status_light = "⚪" 
    
    if item_index in st.session_state.retry_queue:
        status_light = "🔴" 
    elif st.session_state.answered.get(item_index) is True:
        status_light = "🟢" 
    elif st.session_state.answered.get(item_index) is False:
        status_light = "🟡" 
    
    stats_list.append({
        "狀態": status_light,
        "錯誤字詞": tag, 
        "正確/總次數": rate
    })
df_stats = pd.DataFrame(stats_list)
st.sidebar.dataframe(df_stats, use_container_width=True)