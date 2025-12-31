import React, { useState, useEffect, useRef } from "react"
import {Volume2, CheckCircle, XCircle, Star, Award, BarChart3, X} from 'lucide-react'

interface WordItem {
  word: string
  translation: string
  sentence: string
  sentence_zh: string
  definition: string
  definition_zh: string
  blank_index: number
}

interface Stats {
  correct: number
  wrong: number
}

interface HistoryItem {
  mode: string
  questionNumber: number
  word: string
  input: string
  result: string
  time: string
}

type StudyMode = "LEARNING" | "REVIEW"

word_bank = [
    {"word": "agency", "translation": "代辦處;經銷處;政府機構",
     "sentence": "Many people worked at the agency.",
     "sentence_zh": "許多人在這家代辦處工作。",
     "definition": "If you work at an agency, your job is to help others to get something done.",
     "definition_zh": "如果你在一家代辦處工作,你的工作就是幫助別人完成一些事情。",
     "blank_index": 5
     },
    
    {"word": "business", "translation": "生意;業務;商店",
     "sentence": "My aunt opened a small business that sells coffee.",
     "sentence_zh": "我阿姨開了一家賣咖啡的小店。",
     "definition": "A place open for business is ready to work, buy, or sell something.",
     "definition_zh": "一個開放做生意的地方,就是準備好工作、購買或販售某物的場所。",
     "blank_index": 5
     },
     
    {"word": "confidently", "translation": "自信地;有信心地",
     "sentence": "Tia confidently stood up to give her report.",
     "sentence_zh": "Tia 自信地站起來做報告。",
     "definition": "When you do something confidently, you are sure you will do it well.",
     "definition_zh": "當你自信地做某事時,你確信自己能做得很好。",
     "blank_index": 1
     },
     
    {"word": "eagerly", "translation": "熱切地;渴望地",
     "sentence": "The family eagerly explored their new home.",
     "sentence_zh": "這家人熱切地探索他們的新家。",
     "definition": "When you do something eagerly, you really want to do it.",
     "definition_zh": "當你熱切地做某事時,你真的很想做它。",
     "blank_index": 2
     },
     
    {"word": "seeps", "translation": "滲出;緩慢穿過",
     "sentence": "The sand seeps through the hourglass.",
     "sentence_zh": "沙子緩慢地從沙漏中滲出。",
     "definition": "When something seeps, it passes slowly through a small opening.",
     "definition_zh": "當某物滲出時,它會緩慢地穿過一個小開口。",
     "blank_index": 2
     },
     
    {"word": "mystery", "translation": "謎;難以理解的事物",
     "sentence": "The contents of the box are a mystery.",
     "sentence_zh": "箱子裡的內容物是個謎。",
     "definition": "A mystery is something that is hard to understand or is not known about.",
     "definition_zh": "謎是難以理解或不為人知的事物。",
     "blank_index": 7
     },
     
    {"word": "ace", "translation": "高手;一流人才",
     "sentence": "He is an ace athlete.",
     "sentence_zh": "他是一位一流的運動員。",
     "definition": "Someone described as an ace is extremely good at something.",
     "definition_zh": "被描述為高手的人,在某方面是非常優秀的。",
     "blank_index": 3
     },
     
    {"word": "located", "translation": "位於;坐落於",
     "sentence": "The alligator pond was located near the center of the zoo.",
     "sentence_zh": "鱷魚池位於動物園的中心附近。",
     "definition": "Where something is located is where it is.",
     "definition_zh": "某物被定位(located)的地方就是它所在的位置。",
     "blank_index": 4
     },
]

function App() {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [studyMode, setStudyMode] = useState<StudyMode>("LEARNING")
  const [sequenceCursor, setSequenceCursor] = useState(0)
  const [wrongQueue, setWrongQueue] = useState<number[]>([])
  const [stats, setStats] = useState<Stats[]>(
    wordBank.map(() => ({ correct: 0, wrong: 0 }))
  )
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [userInput, setUserInput] = useState("")
  const [lastMessage, setLastMessage] = useState<{
    type: "success" | "error" | "info"
    text: string
    diff?: { correct: string; input: string }
  } | null>(null)
  const [showSidebar, setShowSidebar] = useState(false)
  const [showNextButton, setShowNextButton] = useState(false)
  
  const inputRef = useRef<HTMLInputElement>(null)
  const audioRef = useRef<HTMLAudioElement>(null)
  const correctAudioRef = useRef<HTMLAudioElement | null>(null)

  // Preload correct answer audio
  useEffect(() => {
    correctAudioRef.current = new Audio("https://static.lumi.new/material/f5/f5901670ee5c4ee9a934c52a076ee945.mp3")
    correctAudioRef.current.preload = "auto"
    correctAudioRef.current.load()
  }, [])

  const currentItem = wordBank[currentIndex]
  const totalQuestions = wordBank.length

  // Auto focus input on mount and after question change
  useEffect(() => {
    inputRef.current?.focus()
  }, [currentIndex])

  const playSound = (type: "correct" | "wrong") => {
    if (type === "correct") {
      // 播放答對音效 MP3 (已預加載)
      if (correctAudioRef.current) {
        correctAudioRef.current.currentTime = 0
        correctAudioRef.current.play().catch(err => console.error("播放音效失敗:", err))
      }
    } else {
      // 播放"大黃蜂的飛行"旋律 (3秒)
      // 基於真實樂曲:A小調,主要使用半音階下行跑動
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      const duration = 0.5 // 0.5秒
      const startTime = audioContext.currentTime
      
      // 大黃蜂的飛行 - 真實開場旋律 (A小調,從A5開始半音階下行)
      // 每個八度重複半音階跑動的特徵性模式
      const bumblebeePattern = [
        // 第一組:A5開始半音階快速下降
        880, 831, 784, 740, 698, 659, 622, 587,
        554, 523, 494, 466, 440,
        // 小跳躍後再次下降
        659, 622, 587, 554, 523, 494, 466, 440,
        415, 392, 370, 349, 330,
        // 第二組:較低音域重複
        523, 494, 466, 440, 415, 392, 370, 349,
        330, 311, 294, 277, 262,
        // 第三組:回到中音域
        440, 415, 392, 370, 349, 330, 311, 294,
        277, 262, 247, 233, 220,
        // 結束組:快速半音階上升然後下降
        294, 311, 330, 349, 370, 392, 415, 440,
        466, 494, 523, 554, 587, 622, 659, 698,
        740, 784, 831, 880, 831, 784, 740, 698,
        659, 622, 587, 554, 523, 494, 466, 440
      ]
      
      const noteInterval = 0.04 // 極快的音符切換 (40ms) - 符合原曲超快速度
      const totalNotes = Math.floor(duration / noteInterval)
      
      for (let i = 0; i < totalNotes; i++) {
        const oscillator = audioContext.createOscillator()
        const gainNode = audioContext.createGain()
        
        oscillator.connect(gainNode)
        gainNode.connect(audioContext.destination)
        
        // 循環使用大黃蜂旋律
        const noteIndex = i % bumblebeePattern.length
        oscillator.frequency.value = bumblebeePattern[noteIndex]
        oscillator.type = "triangle" // 三角波 - 接近弦樂音色
        
        // 快速斷奏效果
        const time = startTime + (i * noteInterval)
        gainNode.gain.setValueAtTime(0.15, time)
        gainNode.gain.exponentialRampToValueAtTime(0.01, time + noteInterval * 0.8)
        
        oscillator.start(time)
        oscillator.stop(time + noteInterval)
      }
    }
  }

  const speak = (text: string, lang: string = "en-US") => {
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = lang
    utterance.rate = 0.9
    window.speechSynthesis.cancel()
    window.speechSynthesis.speak(utterance)
  }

  const getDiffHtml = (correct: string, input: string) => {
    const a = correct.toLowerCase()
    const b = input.toLowerCase()
    
    let i = 0
    let j = 0
    const correctChars: Array<{ char: string; status: "correct" | "wrong" | "missing" }> = []
    const inputChars: Array<{ char: string; status: "correct" | "wrong" | "extra" }> = []
    
    while (i < a.length || j < b.length) {
      if (i < a.length && j < b.length && a[i] === b[j]) {
        correctChars.push({ char: a[i], status: "correct" })
        inputChars.push({ char: b[j], status: "correct" })
        i++
        j++
      } else if (i < a.length && j >= b.length) {
        correctChars.push({ char: a[i], status: "missing" })
        inputChars.push({ char: "_", status: "extra" })
        i++
      } else if (j < b.length && i >= a.length) {
        correctChars.push({ char: "_", status: "missing" })
        inputChars.push({ char: b[j], status: "extra" })
        j++
      } else {
        correctChars.push({ char: a[i], status: "wrong" })
        inputChars.push({ char: b[j], status: "wrong" })
        i++
        j++
      }
    }
    
    return { correctChars, inputChars }
  }

  const goNextQuestion = () => {
    if (studyMode === "REVIEW") {
      if (wrongQueue.length > 0) {
        const nextIdx = wrongQueue[0]
        setCurrentIndex(nextIdx)
      } else {
        setStudyMode("LEARNING")
        setSequenceCursor(0)
        setCurrentIndex(0)
        setLastMessage({
          type: "success",
          text: "🎉 錯題複習完畢!開始新的一輪!"
        })
      }
    } else if (studyMode === "LEARNING") {
      const nextCursor = sequenceCursor + 1
      setSequenceCursor(nextCursor)
      
      if (nextCursor < totalQuestions) {
        setCurrentIndex(nextCursor)
      } else {
        if (wrongQueue.length > 0) {
          setStudyMode("REVIEW")
          setLastMessage({
            type: "info",
            text: "🔄 一輪結束,進入錯題複習模式!"
          })
          setCurrentIndex(wrongQueue[0])
        } else {
          setSequenceCursor(0)
          setCurrentIndex(0)
          setLastMessage({
            type: "success",
            text: "💯 太強了!全部答對,直接開始新的一輪!"
          })
        }
      }
    }
    setUserInput("")
    setLastMessage(null)
    setShowNextButton(false)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    const userText = userInput.trim().toLowerCase()
    const correctWord = currentItem.word.toLowerCase()
    const isCorrect = userText === correctWord
    
    const now = new Date().toLocaleString("zh-TW", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit"
    })
    
    if (isCorrect) {
      playSound("correct")
      setStats(prev => {
        const newStats = [...prev]
        newStats[currentIndex].correct++
        return newStats
      })
      const diff = getDiffHtml(currentItem.word, userText)
      setLastMessage({
        type: "success",
        text: "✅ 答對了!",
        diff: {
          correct: JSON.stringify(diff.correctChars),
          input: JSON.stringify(diff.inputChars)
        }
      })
      setWrongQueue(prev => prev.filter(idx => idx !== currentIndex))
    } else {
      playSound("wrong")
      setStats(prev => {
        const newStats = [...prev]
        newStats[currentIndex].wrong++
        return newStats
      })
      
      const diff = getDiffHtml(currentItem.word, userText)
      setLastMessage({
        type: "error",
        text: userText 
          ? `❌ 答錯!正確答案是: ${currentItem.word} (你的輸入: ${userText})`
          : `⭐️ 跳過!正確答案是: ${currentItem.word}`,
        diff: {
          correct: JSON.stringify(diff.correctChars),
          input: JSON.stringify(diff.inputChars)
        }
      })
      
      if (!wrongQueue.includes(currentIndex)) {
        setWrongQueue(prev => [...prev, currentIndex])
      } else if (studyMode === "REVIEW" && wrongQueue[0] === currentIndex) {
        setWrongQueue(prev => [...prev.slice(1), prev[0]])
      }
    }
    
    setHistory(prev => [{
      mode: studyMode === "REVIEW" ? "複習" : "一般",
      questionNumber: currentIndex + 1,
      word: currentItem.word,
      input: userInput,
      result: isCorrect ? "正確" : "錯誤",
      time: now
    }, ...prev])
    
    setShowNextButton(true)
  }

  const renderSentenceWithBlank = () => {
    const words = currentItem.sentence.split(" ")
    const result: React.ReactNode[] = []
    
    words.forEach((word, idx) => {
      if (idx === currentItem.blank_index) {
        // Extract punctuation if any
        const punctuation = word.match(/[.,!?;:]$/)?.[0] || ""
        result.push(
          <span key={idx} className="inline-flex items-center gap-1">
            <span className="inline-block w-40 h-12 border-b-4 border-blue-400"></span>
            {punctuation && <span>{punctuation}</span>}
          </span>
        )
      } else {
        result.push(<span key={idx}>{word} </span>)
      }
    })
    
    return result
  }

  const renderDiffChars = (charsJson: string, type: "correct" | "input") => {
    try {
      const chars = JSON.parse(charsJson) as Array<{ char: string; status: string }>
      return chars.map((item, idx) => {
        let bgColor = "#ddffdd"
        let textColor = "#000"
        
        if (item.status === "wrong") {
          bgColor = "#b22222"
          textColor = "#fff"
        } else if (item.status === "missing" || item.status === "extra") {
          bgColor = "#eeeeee"
          textColor = "#888"
        }
        
        return (
          <span
            key={idx}
            className="inline-flex items-center justify-center"
            style={{
              width: "20px",
              height: "32px",
              margin: "1px",
              borderRadius: "4px",
              backgroundColor: bgColor,
              color: textColor,
              fontSize: "36px",
              fontWeight: "bold",
              fontFamily: "monospace",
              lineHeight: "27px"
            }}
          >
            {item.char}
          </span>
        )
      })
    } catch {
      return null
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white shadow-sm p-4">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-xl">🎧</span>
              </div>
              <h1 className="text-2xl font-bold text-gray-800">單字填空練習</h1>
            </div>
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="flex items-center gap-2 px-4 py-2 bg-white text-black border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition-all shadow-md"
            >
              <BarChart3 size={20} />
              <span className="text-sm font-medium">統計</span>
            </button>
          </div>
        </header>

        {/* Study Mode Indicator */}
        {studyMode === "REVIEW" && (
          <div className="bg-orange-100 border-l-4 border-orange-500 p-2 max-w-4xl mx-auto w-full mt-2">
            <p className="text-orange-700 font-semibold">
              🔥 錯題複習模式 (剩餘 {wrongQueue.length} 題)
            </p>
          </div>
        )}

        {/* Message Display */}
        {lastMessage && (
          <div className={`max-w-4xl mx-auto w-full p-2 rounded-t-lg border-l-4 ${
            lastMessage.type === "success" 
              ? "bg-green-50 border-green-500" 
              : lastMessage.type === "error"
              ? "bg-red-50 border-red-500"
              : "bg-blue-50 border-blue-500"
          }`}>
            <p className="text-sm font-medium mb-1">{lastMessage.text}</p>
            {lastMessage.diff && (
              <div className="text-center mt-0">
                <div className="flex justify-center gap-1 mb-0">
                  {renderDiffChars(lastMessage.diff.correct, "correct")}
                </div>
                <div className="text-xs text-gray-500 my-0">⬇️</div>
                <div className="flex justify-center gap-1">
                  {renderDiffChars(lastMessage.diff.input, "input")}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Main Question Area */}
        <main className="flex-1 flex items-center justify-center pt-0 px-3 pb-3">
          <div className="max-w-4xl w-full bg-black rounded-2xl shadow-xl p-6">
            {/* Sentence Display */}
            <div className="text-center mb-0">
              <p className="text-4xl font-black text-yellow-400 leading-relaxed flex flex-wrap items-center justify-center gap-2">
                {renderSentenceWithBlank()}
              </p>
            </div>

            {/* Input Form or Next Button */}
            {!showNextButton ? (
              <form onSubmit={handleSubmit} className="space-y-1">
                <div className="flex justify-center">
                  <input
                    ref={inputRef}
                    type="text"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    placeholder="輸入單字..."
                    className="w-full max-w-xs px-4 py-3 text-xl font-semibold text-center text-blue-600 bg-white border-4 border-blue-400 rounded-xl focus:outline-none focus:border-blue-600 focus:bg-blue-50 transition-all shadow-md"
                    autoComplete="off"
                  />
                </div>

                {/* Audio Buttons */}
                <div className="flex items-center justify-center gap-0 mb-1">
                  <img 
                    src="https://static.lumi.new/b2/b28b46748c31efe0fdfff7fc3ce3ec4f.webp" 
                    alt="Duolingo Owl"
                    className="w-20 h-20 object-contain"
                  />
                  <div className="grid grid-cols-3 gap-2">
                    <button
                      type="button"
                      onClick={() => speak(currentItem.word, "en-US")}
                      className="flex items-center justify-center gap-1 px-1 py-2 bg-green-500 text-white rounded-lg hover:bg-green-400 transition-all text-sm w-20"
                    >
                      <Volume2 size={16} />
                      <span className="font-medium">單字(英)</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => speak(currentItem.sentence, "en-US")}
                      className="flex items-center justify-center gap-1 px-1 py-2 bg-green-500 text-white rounded-lg hover:bg-green-400 transition-all text-sm w-20"
                    >
                      <Volume2 size={16} />
                      <span className="font-medium">例句(英)</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => speak(currentItem.definition, "en-US")}
                      className="flex items-center justify-center gap-1 px-1 py-2 bg-green-500 text-white rounded-lg hover:bg-green-400 transition-all text-sm w-20"
                    >
                      <Volume2 size={16} />
                      <span className="font-medium">定義(英)</span>
                    </button>
                  </div>
                </div>

                <div className="flex justify-center">
                  <button
                    type="submit"
                    className="flex items-center justify-center gap-1 px-1 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-all text-sm w-20"
                  >
                    ✓ 檢查答案
                  </button>
                </div>
              </form>
            ) : (
              <div className="flex justify-center mt-0">
                <button
                  onClick={goNextQuestion}
                  className="px-8 py-4 bg-red-500 text-white text-xl font-bold rounded-2xl hover:bg-red-600 active:bg-red-700 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1 active:translate-y-0 flex items-center justify-center gap-2"
                >
                  <span className="text-sm">➡️</span>
                  <span>下一題</span>
                </button>
              </div>
            )}

            {/* Translations & Definitions */}
            <div className="mt-4 space-y-2 text-white">
              <p><span className="font-semibold">中文單字翻譯:</span> {currentItem.translation}</p>
              <p><span className="font-semibold">中文翻譯:</span> <em>{currentItem.sentence_zh}</em></p>
              <p><span className="font-semibold">英文定義:</span> <em>{currentItem.definition}</em></p>
              <p><span className="font-semibold">中文定義:</span> <em>{currentItem.definition_zh}</em></p>
            </div>
          </div>
        </main>
      </div>

      {/* Sidebar - Toggle Visibility */}
      <aside className={`${showSidebar ? "w-96" : "w-0"} transition-all duration-300 overflow-hidden bg-white shadow-2xl`}>
        <div className="p-6 w-96">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-800">📊 練習統計</h2>
            <button
              onClick={() => setShowSidebar(false)}
              className="text-gray-500 hover:text-gray-700 transition-colors"
            >
              <X size={24} />
            </button>
          </div>

          {/* Current Status */}
          <div className="mb-6 p-4 bg-indigo-50 rounded-lg">
            <p className="text-sm text-gray-600">目前模式: <span className="font-bold">{studyMode}</span></p>
            <p className="text-sm text-gray-600">待複習錯題數: <span className="font-bold text-red-600">{wrongQueue.length}</span></p>
          </div>

          {/* Word Statistics */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">📈 單字答題統計</h3>
            <div className="space-y-2">
              {wordBank.map((item, idx) => {
                const stat = stats[idx]
                const total = stat.correct + stat.wrong
                const rate = total > 0 ? `${stat.correct}/${total}` : "0/0"
                
                let statusIcon = "⚪"
                if (wrongQueue.includes(idx)) {
                  statusIcon = "🔴"
                } else if (stat.correct > 0) {
                  statusIcon = "🟢"
                } else if (stat.wrong > 0) {
                  statusIcon = "🟡"
                }
                
                return (
                  <div key={idx} className="flex items-center gap-2 p-2 bg-gray-50 rounded text-sm">
                    <span>{statusIcon}</span>
                    <span className="font-medium w-8">#{idx + 1}</span>
                    <span className="flex-1 truncate">{item.word}</span>
                    <span className="font-semibold text-indigo-600">{rate}</span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* History */}
          <div>
            <h3 className="text-lg font-semibold mb-3">📝 歷史紀錄</h3>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {history.slice(0, 20).map((item, idx) => (
                <div key={idx} className={`p-2 rounded text-xs ${
                  item.result === "正確" ? "bg-green-50" : "bg-red-50"
                }`}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-semibold">
                      {item.result === "正確" ? <CheckCircle size={14} className="inline text-green-600" /> : <XCircle size={14} className="inline text-red-600" />}
                      {" "}#{item.questionNumber} {item.word}
                    </span>
                    <span className="text-gray-500">{item.mode}</span>
                  </div>
                  <p className="text-gray-600">輸入: {item.input || "(空白)"}</p>
                  <p className="text-gray-400 text-xs">{item.time}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </aside>
    </div>
  )
}

export default App
