import React, { useState, useEffect, useRef } from "react"
import { Volume2, SkipForward, BarChart3, BookOpen, Target } from 'lucide-react'
import toast, { Toaster } from "react-hot-toast"

// 詞彙列表
const chineseWords = [
  "黑皮鞋", "穿戴", "面具", "起飛", "舞者",
  "海洋", "寒冷", "北方", "扁平", "張嘴",
  "伸長", "溫飽", "沙子", "著急", "衣服",
  "站立", "翅膀", "陽光", "充滿", "思念"
]

interface WordStats {
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

function App() {
  const [studyMode, setStudyMode] = useState<StudyMode>("LEARNING")
  const [sequenceCursor, setSequenceCursor] = useState(0)
  const [currentDisplayIndex, setCurrentDisplayIndex] = useState(0)
  const [wrongQueue, setWrongQueue] = useState<number[]>([])
  const [stats, setStats] = useState<WordStats[]>(
    chineseWords.map(() => ({ correct: 0, wrong: 0 }))
  )
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [userInput, setUserInput] = useState("")
  const [showResult, setShowResult] = useState(false)
  const [lastResult, setLastResult] = useState<{ isCorrect: boolean; diff: string } | null>(null)
  const [showSidebar, setShowSidebar] = useState(false)
  
  const inputRef = useRef<HTMLInputElement>(null)
  
  // --- 語音系統變數 ---
  const synth = typeof window !== "undefined" ? window.speechSynthesis : null
  const voicesRef = useRef<SpeechSynthesisVoice[]>([])

  // 音效 Audio 元素 (正確/錯誤提示音)
  const correctSound = useRef<HTMLAudioElement | null>(null)
  const wrongSound = useRef<HTMLAudioElement | null>(null)

  const currentWord = chineseWords[currentDisplayIndex]

  // 初始化音效與語音引擎
  useEffect(() => {
    // 預載提示音
    correctSound.current = new Audio("https://static.lumi.new/material/f5/f5901670ee5c4ee9a934c52a076ee945.mp3")
    wrongSound.current = new Audio("https://static.lumi.new/material/d5/d59fce81a6ec4629dca550ecc81a4892.mp3")

    const loadVoices = () => {
      if (synth) {
        const availableVoices = synth.getVoices()
        voicesRef.current = availableVoices
        console.log("語音清單已更新，可用數量:", availableVoices.length)
      }
    }

    if (synth) {
      loadVoices()
      // 行動端瀏覽器語音包通常非同步載入，需監聽此事件
      if (synth.onvoiceschanged !== undefined) {
        synth.onvoiceschanged = loadVoices
      }
    }
  }, [synth])

  // 播放提示音效
  const playSound = (type: "correct" | "wrong") => {
    const audio = type === "correct" ? correctSound.current : wrongSound.current
    if (audio) {
      audio.currentTime = 0
      audio.play().catch(e => console.log("音效播放被攔截:", e))
      
      if (type === "wrong") {
        setTimeout(() => {
          audio.pause()
          audio.currentTime = 0
        }, 1000)
      }
    }
  }

  // --- 核心：台灣繁體中文播放邏輯 ---
  const startSpeech = (text: string) => {
    if (!synth) return

    // 解決部分行動裝置(平板)語音引擎掛起的問題
    synth.cancel()
    synth.resume() 

    const utterance = new SpeechSynthesisUtterance(text)
    const voices = voicesRef.current.length > 0 ? voicesRef.current : synth.getVoices()

    // 優先搜尋台灣語音包 (如 iOS 的 Mei-Jia 或 Google 的 zh-TW)
    const taiwanVoice = voices.find(v => 
      (v.lang === 'zh-TW' || v.lang === 'zh_TW') && 
      (v.name.includes('Taiwan') || v.name.includes('TW') || v.name.includes('Mei-Jia') || v.name.includes('Traditional'))
    ) || voices.find(v => v.lang.startsWith('zh-TW') || v.lang.startsWith('zh_TW'))
      || voices.find(v => v.lang.includes('zh'));

    if (taiwanVoice) {
      utterance.voice = taiwanVoice
      utterance.lang = taiwanVoice.lang
    } else {
      utterance.lang = "zh-TW"
    }

    // 設定適合學習的台灣發音參數
    utterance.rate = 0.8  // 語速稍微放慢
    utterance.pitch = 1.0 // 音調自然
    utterance.volume = 1.0

    utterance.onstart = () => {
      toast.success("🔊 正在播放", { id: "tts-toast", duration: 800 })
    }

    synth.speak(utterance)
  }

  const playTTS = (text: string) => {
    try {
      if (!synth) {
        toast.error("❌ 此裝置不支援語音功能")
        return
      }
      startSpeech(text)
    } catch (error) {
      console.error("TTS Error:", error)
    }
  }

  // 輔助：比對輸入差異的顯示
  const getDiffDisplay = (correct: string, input: string) => {
    const correctChars = correct.split("")
    const inputChars = input.split("")
    const maxLen = Math.max(correctChars.length, inputChars.length)
    
    const renderChars = (chars: string[], isInput: boolean) => (
      <div>
        {Array.from({ length: maxLen }).map((_, i) => {
          const char = chars[i] || "_"
          const targetChar = isInput ? correctChars[i] : inputChars[i]
          const isMatch = char !== "_" && char === (isInput ? correctChars[i] : inputChars[i])
          
          let bgColor = "bg-red-500"
          if (isMatch) bgColor = "bg-green-500"
          if (char === "_") bgColor = "bg-gray-300"

          return (
            <span key={i} className={`inline-flex items-center justify-center w-10 h-12 m-0.5 rounded-lg ${bgColor} text-white font-bold text-2xl`}>
              {char}
            </span>
          )
        })}
      </div>
    )

    return (
      <div className="my-4 space-y-2">
        {renderChars(correctChars, false)}
        <div className="text-gray-400 text-center text-sm">VS</div>
        {renderChars(inputChars, true)}
      </div>
    )
  }

  // 下一題邏輯
  const goNextQuestion = () => {
    if (studyMode === "REVIEW") {
      if (wrongQueue.length > 0) {
        setCurrentDisplayIndex(wrongQueue[0])
      } else {
        setStudyMode("LEARNING")
        setSequenceCursor(0)
        setCurrentDisplayIndex(0)
        toast.success("🎉 錯題複習完成！")
      }
    } else {
      const nextCursor = sequenceCursor + 1
      if (nextCursor < chineseWords.length) {
        setSequenceCursor(nextCursor)
        setCurrentDisplayIndex(nextCursor)
      } else if (wrongQueue.length > 0) {
        setStudyMode("REVIEW")
        setCurrentDisplayIndex(wrongQueue[0])
        toast("進入錯題複習模式", { icon: "🔥" })
      } else {
        setSequenceCursor(0)
        setCurrentDisplayIndex(0)
        toast.success("全部完成！新的一輪開始")
      }
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const trimmedInput = userInput.trim()
    if (!trimmedInput && !showResult) {
      handleSkip()
      return
    }

    const isCorrect = trimmedInput === currentWord
    
    // 更新統計
    const newStats = [...stats]
    if (isCorrect) newStats[currentDisplayIndex].correct += 1
    else newStats[currentDisplayIndex].wrong += 1
    setStats(newStats)

    // 更新錯題佇列
    if (isCorrect) {
      setWrongQueue(prev => prev.filter(idx => idx !== currentDisplayIndex))
    } else {
      if (!wrongQueue.includes(currentDisplayIndex)) {
        setWrongQueue(prev => [...prev, currentDisplayIndex])
      }
    }

    // 紀錄歷史
    setHistory(prev => [{
      mode: studyMode === "REVIEW" ? "複習" : "一般",
      questionNumber: currentDisplayIndex + 1,
      word: currentWord,
      input: trimmedInput,
      result: isCorrect ? "正確" : "錯誤",
      time: new Date().toLocaleTimeString()
    }, ...prev])

    setLastResult({ isCorrect, diff: trimmedInput })
    setShowResult(true)
    playSound(isCorrect ? "correct" : "wrong")
  }

  const handleNext = () => {
    setShowResult(false)
    setLastResult(null)
    setUserInput("")
    goNextQuestion()
  }

  const handleSkip = () => {
    setLastResult({ isCorrect: false, diff: "" })
    setShowResult(true)
    playSound("wrong")
  }

  // 自動聚焦
  useEffect(() => {
    if (!showResult && inputRef.current) {
      inputRef.current.focus()
    }
  }, [currentDisplayIndex, showResult])

  return (
    <div className="min-h-screen bg-gray-100 flex font-sans">
      <Toaster position="top-center" />
      
      {/* 側邊欄 */}
      <div className={`fixed inset-y-0 left-0 transform ${showSidebar ? "translate-x-0" : "-translate-x-full"} transition-transform duration-300 ease-in-out z-50 w-80 bg-white shadow-2xl overflow-y-auto`}>
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-black text-blue-600">學習進度</h2>
            <button onClick={() => setShowSidebar(false)} className="text-3xl text-gray-400">&times;</button>
          </div>
          
          <div className="space-y-4">
             <div className="bg-blue-600 text-white p-4 rounded-2xl shadow-lg">
                <div className="text-sm opacity-80">當前模式</div>
                <div className="text-xl font-bold">{studyMode === "LEARNING" ? "📖 一般學習" : "🔥 錯題複習"}</div>
                <div className="mt-2 text-xs">待複習：{wrongQueue.length} 題</div>
             </div>

             <div className="grid grid-cols-2 gap-2">
                <div className="bg-green-50 p-3 rounded-xl border border-green-100">
                   <div className="text-xs text-green-600">累計正確</div>
                   <div className="text-xl font-bold text-green-700">{stats.reduce((a, b) => a + b.correct, 0)}</div>
                </div>
                <div className="bg-red-50 p-3 rounded-xl border border-red-100">
                   <div className="text-xs text-red-600">累計錯誤</div>
                   <div className="text-xl font-bold text-red-700">{stats.reduce((a, b) => a + b.wrong, 0)}</div>
                </div>
             </div>

             <div className="text-sm font-bold text-gray-500 mt-4 flex items-center gap-2"><Target size={16}/> 詞彙列表</div>
             <div className="space-y-1">
                {chineseWords.map((word, idx) => (
                  <div key={idx} className={`p-2 rounded-lg text-sm flex justify-between ${idx === currentDisplayIndex ? "bg-blue-100 border-l-4 border-blue-500" : "bg-gray-50"}`}>
                    <span>{idx + 1}. {word}</span>
                    <span className="text-gray-400">{stats[idx].correct}/{stats[idx].correct + stats[idx].wrong}</span>
                  </div>
                ))}
             </div>
          </div>
        </div>
      </div>

      {/* 主內容 */}
      <div className="flex-1 flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-xl">
          <div className="flex justify-between items-center mb-6">
             <h1 className="text-2xl font-black text-gray-800 flex items-center gap-2">
               <span className="bg-blue-500 text-white p-2 rounded-lg">聽</span> 繁體中文聽力
             </h1>
             <button onClick={() => setShowSidebar(true)} className="p-3 bg-white rounded-2xl shadow-sm hover:shadow-md transition-shadow">
               <BarChart3 className="text-gray-600" />
             </button>
          </div>

          <div className="bg-white rounded-[2.5rem] shadow-xl p-8 border-t-8 border-blue-500 relative overflow-hidden">
            {/* 裝飾 */}
            <div className="absolute top-0 right-0 p-4 text-gray-100 font-black text-6xl select-none">
              {currentDisplayIndex + 1}
            </div>

            <div className="relative z-10">
              <div className="flex flex-col items-center mb-10">
                <div className="text-7xl mb-6 animate-bounce">🦉</div>
                <button
                  onClick={() => playTTS(currentWord)}
                  className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-black py-5 rounded-3xl shadow-xl flex items-center justify-center gap-3 transition-all active:scale-95 mb-2"
                >
                  <Volume2 size={32} />
                  <span className="text-2xl">播放發音</span>
                </button>
                <p className="text-gray-400 text-sm">點擊上方按鈕聆聽台灣繁體中文發音</p>
              </div>

              {showResult && lastResult ? (
                <div className="bg-gray-50 rounded-3xl p-6 border-2 border-dashed border-gray-200 animate-in fade-in zoom-in duration-300">
                  <div className={`text-center font-black text-2xl mb-4 ${lastResult.isCorrect ? "text-green-600" : "text-red-600"}`}>
                    {lastResult.isCorrect ? "✨ 太棒了，完全正確！" : "💡 再接再厲，正確答案是："}
                  </div>
                  
                  {!lastResult.isCorrect && (
                    <div className="flex flex-col items-center">
                      <div className="text-4xl font-black text-gray-800 mb-4">{currentWord}</div>
                      {lastResult.diff && getDiffDisplay(currentWord, lastResult.diff)}
                    </div>
                  )}

                  <button 
                    onClick={handleNext} 
                    className="w-full bg-gray-800 hover:bg-black text-white font-bold py-4 rounded-2xl mt-4 transition-colors"
                  >
                    下一題
                  </button>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="relative">
                    <input
                      ref={inputRef}
                      type="text"
                      value={userInput}
                      onChange={(e) => setUserInput(e.target.value)}
                      placeholder="請輸入你聽到的詞彙..."
                      className="w-full px-6 py-5 text-2xl font-bold bg-gray-50 border-2 border-gray-100 rounded-3xl focus:border-blue-500 focus:bg-white transition-all outline-none"
                      autoComplete="off"
                    />
                  </div>
                  <div className="flex gap-3">
                    <button type="submit" className="flex-1 bg-green-500 hover:bg-green-600 text-white font-black py-4 rounded-2xl shadow-lg transition-transform active:scale-95">
                      提交答案
                    </button>
                    <button type="button" onClick={handleSkip} className="px-6 bg-gray-100 hover:bg-gray-200 text-gray-500 font-bold rounded-2xl transition-colors">
                      跳過
                    </button>
                  </div>
                </form>
              )}

              <div className="mt-8 flex justify-between items-center text-xs font-bold text-gray-300 tracking-widest uppercase">
                <span>PROGRESS: {currentDisplayIndex + 1} / {chineseWords.length}</span>
                <span>TAIWAN TTS ENGINE READY</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 遮罩 */}
      {showSidebar && <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 transition-opacity" onClick={() => setShowSidebar(false)} />}
    </div>
  )
}

export default App