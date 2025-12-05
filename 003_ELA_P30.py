import streamlit as st
import datetime
import pandas as pd
# 引入 os 用來檢查本地音檔路徑
import os 
# 引入 gTTS 來生成語音，以及 io 來處理音訊數據流
from gtts import gTTS
import io


word_bank = [
    # --- High Frequency Words ---
    {"word": "baby", "translation": "嬰兒",
     "sentence": "The baby started to cry loudly.",
     "sentence_zh": "那個嬰兒開始大聲哭泣。",
     "definition": "A very young child.",
     "definition_zh": "一個非常小的孩子。"},

    {"word": "bird", "translation": "鳥",
     "sentence": "A small bird landed on the window sill.",
     "sentence_zh": "一隻小鳥降落在窗台上。",
     "definition": "A warm-blooded egg-laying vertebrate distinguished by the possession of feathers, wings, and a beak.",
     "definition_zh": "一種以擁有羽毛、翅膀和鳥喙為特徵的溫血、卵生脊椎動物。"},

    {"word": "blue", "translation": "藍色的",
     "sentence": "The sky was a bright blue this morning.",
     "sentence_zh": "今天早上的天空是明亮的藍色。",
     "definition": "Of a color intermediate between green and violet, as of the sky or sea on a sunny day.",
     "definition_zh": "介於綠色和紫色之間的一種顏色，如晴天時的天空或海洋的顏色。"},

    {"word": "bring", "translation": "帶來",
     "sentence": "Please remember to bring your book to class.",
     "sentence_zh": "請記得把你的書帶到課堂上。",
     "definition": "To take or go with (someone or something) to a place.",
     "definition_zh": "帶著（某人或某物）去一個地方。"},

    {"word": "fly", "translation": "飛",
     "sentence": "The birds fly south for the winter.",
     "sentence_zh": "這些鳥兒向南飛過冬。",
     "definition": "To move through the air using wings.",
     "definition_zh": "使用翅膀在空氣中移動。"},

    {"word": "her", "translation": "她的；她（受格）",
     "sentence": "She gave her sister a new toy.",
     "sentence_zh": "她給了她妹妹一個新玩具。",
     "definition": "The objective case of she; used as the object of a verb or preposition.",
     "definition_zh": "she 的受格；用作動詞或介系詞的受詞。"},

    {"word": "little", "translation": "小的；少量的",
     "sentence": "There is a little dog next door.",
     "sentence_zh": "隔壁有一隻小狗。",
     "definition": "Small in size, amount, or degree.",
     "definition_zh": "在尺寸、數量或程度上小。"},

    {"word": "place", "translation": "地方；放置",
     "sentence": "Let's find a place to sit down.",
     "sentence_zh": "我們找個地方坐下吧。",
     "definition": "A particular position or point in space.",
     "definition_zh": "空間中一個特定的位置或點。"},

    {"word": "she", "translation": "她",
     "sentence": "She is going to the park this afternoon.",
     "sentence_zh": "她今天下午要去公園。",
     "definition": "Used to refer to a woman, girl, or female animal previously mentioned or easily identified.",
     "definition_zh": "用於指代先前提到或容易識別的女性、女孩或雌性動物。"},

    {"word": "this", "translation": "這個；這",
     "sentence": "This is my favorite book.",
     "sentence_zh": "這是我最喜歡的書。",
     "definition": "Used to identify a specific person or thing close at hand or being indicated or experienced.",
     "definition_zh": "用於識別近在眼前或正在被指示或經歷的特定人物或事物。"},

    # --- Spelling Words: List 6 (Beginning Blends with l, r, s) ---
    {"word": "space", "translation": "空間；太空",
     "sentence": "We need more space to store the boxes.",
     "sentence_zh": "我們需要更多空間來存放這些箱子。",
     "definition": "A continuous area or expanse which is free, available, or unoccupied.",
     "definition_zh": "一個連續的區域或範圍，它是自由的、可用的或未被佔據的。"},

    {"word": "globe", "translation": "地球儀；球體",
     "sentence": "She pointed to Australia on the classroom globe.",
     "sentence_zh": "她指著教室地球儀上的澳洲。",
     "definition": "A spherical object; a sphere on which a map of the world is represented.",
     "definition_zh": "一個球形物體；一個上面繪製有世界地圖的球體。"},

    {"word": "grade", "translation": "年級；分數；等級",
     "sentence": "He is in the first grade at school.",
     "sentence_zh": "他在學校讀一年級。",
     "definition": "A level of study in an educational institution.",
     "definition_zh": "教育機構中的一個學習級別。"},

    {"word": "swim", "translation": "游泳",
     "sentence": "Can you swim in the ocean?",
     "sentence_zh": "你能在海裡游泳嗎？",
     "definition": "Propel the body through water by means of the limbs or tail.",
     "definition_zh": "通過四肢或尾巴在水中推動身體。"},

    {"word": "last", "translation": "最後的；持續",
     "sentence": "This is the last cookie in the jar.",
     "sentence_zh": "這是罐子裡最後一塊餅乾了。",
     "definition": "Coming after all others in time or order; final.",
     "definition_zh": "在時間或順序上排在所有其他之後；最終的。"},

    {"word": "test", "translation": "測驗；檢驗",
     "sentence": "The students prepared for their math test.",
     "sentence_zh": "學生們為他們的數學測驗做準備。",
     "definition": "A procedure intended to establish the quality, performance, or reliability of something.",
     "definition_zh": "旨在確定某物的品質、性能或可靠性的程序。"},

    {"word": "skin", "translation": "皮膚",
     "sentence": "Protect your skin from the sun.",
     "sentence_zh": "保護你的皮膚免受陽光照射。",
     "definition": "The thin layer of tissue forming the natural outer covering of the body of a person or animal.",
     "definition_zh": "構成人或動物身體自然外層覆蓋物的薄層組織。"},

    {"word": "drag", "translation": "拖曳",
     "sentence": "He had to drag the heavy box across the floor.",
     "sentence_zh": "他不得不拖著那個沉重的箱子穿過地板。",
     "definition": "Pull (someone or something) along forcefully, roughly, or with difficulty.",
     "definition_zh": "用力、粗暴地或困難地拖拉（某人或某物）。"},

    {"word": "glide", "translation": "滑行；悄悄地移動",
     "sentence": "The eagle began to glide on the wind currents.",
     "sentence_zh": "老鷹開始在氣流上滑翔。",
     "definition": "To move with a smooth, continuous motion.",
     "definition_zh": "以平穩、連續的動作移動。"},

    {"word": "just", "translation": "只是；剛才；公正的",
     "sentence": "I just finished my homework.",
     "sentence_zh": "我剛才完成了我的家庭作業。",
     "definition": "Exactly; precisely.",
     "definition_zh": "確切地；精確地。"},

    {"word": "stove", "translation": "爐子；火爐",
     "sentence": "She cooked dinner on the electric stove.",
     "sentence_zh": "她在電爐上煮晚餐。",
     "definition": "An apparatus for heating or cooking, consisting of a heated chamber or firebox.",
     "definition_zh": "一種用於加熱或烹飪的設備，由一個加熱的腔室或火箱組成。"},

    # --- Review Words / Challenge Words ---
    {"word": "slid", "translation": "滑動（slide的過去式）",
     "sentence": "He slid on the ice and fell down.",
     "sentence_zh": "他在冰上滑倒了。",
     "definition": "Past tense of slide: move along a smooth surface while maintaining continuous contact with it.",
     "definition_zh": "slide 的過去式：沿著光滑的表面移動，同時與其保持持續接觸。"},

    {"word": "close", "translation": "關閉；近的",
     "sentence": "Please close the door when you leave.",
     "sentence_zh": "請在你離開時把門關上。",
     "definition": "Move (something) so that an opening or passage is covered or obstructed; near.",
     "definition_zh": "移動（某物）使開口或通道被覆蓋或阻塞；近的。"},

    {"word": "grape", "translation": "葡萄",
     "sentence": "The basket was full of fresh green grapes.",
     "sentence_zh": "籃子裡裝滿了新鮮的綠葡萄。",
     "definition": "A berry (typically green, purple, red, or black) growing in clusters on a vine, eaten as fruit, or used to make wine.",
     "definition_zh": "一種生長在藤蔓上的漿果（通常是綠色、紫色、紅色或黑色），作為水果食用，或用於釀酒。"},

    {"word": "plate", "translation": "盤子；碟子",
     "sentence": "He put his sandwich on a clean plate.",
     "sentence_zh": "他把他的三明治放在一個乾淨的盤子上。",
     "definition": "A flat dish, typically circular and made of china, from which food is eaten.",
     "definition_zh": "一種扁平的碟子，通常是圓形的，由瓷器製成，用於盛放食物。"},

    {"word": "climb", "translation": "攀爬",
     "sentence": "We watched the children climb the tree.",
     "sentence_zh": "我們看著孩子們爬樹。",
     "definition": "Go or move up (something) using the hands and feet.",
     "definition_zh": "使用手和腳向上移動（某物）。"},

    {"word": "bruise", "translation": "瘀傷",
     "sentence": "She fell and got a small bruise on her knee.",
     "sentence_zh": "她跌倒了，膝蓋上有一小塊瘀傷。",
     "definition": "An injury appearing as an area of discolored skin on the body, caused by a blow or impact.",
     "definition_zh": "一種作為身體上皮膚變色區域出現的傷害，由打擊或撞擊引起。"},
]


# --- 播放函式 (處理本地檔案) ---

def play_local_audio(filename: str):
    """
    播放本地上傳的音訊檔案，利用 Streamlit 的 st.audio。
    """
    if not os.path.exists(filename):
        st.warning(f"⚠ 找不到音訊檔案：'{filename}'，請確認檔案是否存在。")
        return
    
    try:
        # 讀取檔案為 bytes 並讓 Streamlit 播放
        audio_bytes = open(filename, 'rb').read()
        # 加上 autoplay=True 使其在頁面加載時自動播放
        
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
sentence = current_item["sentence"]
sentence_zh = current_item["sentence_zh"]
definition = current_item.get("definition", "N/A")
definition_zh = current_item.get("definition_zh", "N/A") 


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
    
    font_size = "24px" 
    
    if "答對了" in message or "複習完畢" in message or "全部答對" in message: 
        
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
    st.warning(f"🔥 錯題複習模式 (剩餘 {len(st.session_state.wrong_queue)} 題)")
else:
    display_progress = st.session_state.sequence_cursor 
    if display_progress == total_questions: display_progress = 0
    st.info(f"📖 順序學習模式 (進度 {display_progress + 1} / {total_questions})")

#st.markdown("<p style='font-size:18px'>📌 發音按鈕 (單字 / 英文例句 / 中文翻譯 / 英文定義 / 中文定義)</p>", unsafe_allow_html=True)
#st.markdown("<p style='font-size:18px'>✏️ 單字測驗</p>", unsafe_allow_html=True)

# --- 發音按鈕 (使用 set_gtts_to_play) ---
col1, col2, col3, col4, col5 = st.columns(5) 
with col1:
    if st.button("▶ 單字（英）"):
        set_gtts_to_play(current_word, 'en')
with col2:
    if st.button("▶ 例句（英）"):
        set_gtts_to_play(sentence, 'en')
#with col3:
#    if st.button("▶ 例句（中）"):
#        set_gtts_to_play(sentence_zh, 'zh-tw')
with col3: 
    if st.button("▶ 定義（英）"):
        set_gtts_to_play(definition, 'en')
#with col5: 
#    if st.button("▶ 定義（中）"):
#        set_gtts_to_play(definition_zh, 'zh-tw')


# 顯示文字 (保持不變)
st.write(f"中文單字翻譯：**{translation}**")
st.write(f"**英文例句：** *{sentence}*")
st.write(f"**中文翻譯：** *{sentence_zh}*")
st.markdown(f"**英文定義：** *{definition}*") 
st.write(f"**中文定義：** *{definition_zh}*") 


# --- 單字答題表單 ---
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
            st.session_state.last_message = "✅ 答對了！" 
            if current_index in st.session_state.wrong_queue:
                st.session_state.wrong_queue.remove(current_index) 
            
            # *** 設定正確音效路徑 (本地音效) ***
            st.session_state.local_sound_to_play = "audio/duolingo_style_correct.mp3" 
            
            # 立即跳下一題 (無延遲)
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
            
            # *** 設定錯誤音效路徑 (本地音效) ***
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

# --- 側邊欄統計 (保持不變) ---
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