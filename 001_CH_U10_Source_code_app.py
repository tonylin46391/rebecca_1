import React, { useState, useEffect, useRef } from "react"
import {Volume2, SkipForward, BarChart3, BookOpen, Target} from 'lucide-react'
import toast, { Toaster } from "react-hot-toast"

// 詞彙列表
const chineseWords = [
  "冷風", "雪梨", "港口", "卻是", "冬天",
  "台灣", "季節", "相反", "煙火", "點心",
  "等待", "綻放", "夜空", "照片", "分享",
  "雖然", "喜歡", "春節", "年貨", "期待", "年夜飯"
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
  const synth = window.speechSynthesis
  
  // 音效 Audio 元素
  const correctSound = useRef<HTMLAudioElement | null>(null)
  const wrongSound = useRef<HTMLAudioElement | null>(null)

  const currentWord = chineseWords[currentDisplayIndex]

  // 初始化音效
  useEffect(() => {
    correctSound.current = new Audio("https://static.lumi.new/material/f5/f5901670ee5c4ee9a934c52a076ee945.mp3")
    wrongSound.current = new Audio("https://static.lumi.new/material/d5/d59fce81a6ec4629dca550ecc81a4892.mp3")
  }, [])

  // 播放音效
  const playSound = (type: "correct" | "wrong") => {
    if (type === "correct" && correctSound.current) {
      correctSound.current.currentTime = 0
      correctSound.current.play().catch(e => console.log("音效播放失敗:", e))
    } else if (type === "wrong" && wrongSound.current) {
      wrongSound.current.currentTime = 0
      wrongSound.current.play().catch(e => console.log("音效播放失敗:", e))
      // 1秒後停止播放
      setTimeout(() => {
        if (wrongSound.current) {
          wrongSound.current.pause()
          wrongSound.current.currentTime = 0
        }
      }, 1000)
    }
  }

  // 自動聚焦輸入框
  useEffect(() => {
    if (!showResult && inputRef.current) {
      inputRef.current.focus()
    }
  }, [currentDisplayIndex, showResult])

  // 進入新題目時自動播放發音
  useEffect(() => {
    if (!showResult) {
      playTTS(currentWord)
    }
  }, [currentDisplayIndex])

  // TTS 語音播放
  const playTTS = (text: string) => {
    if (synth.speaking) {
      synth.cancel()
    }
    
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = "zh-TW"
    utterance.rate = 0.8
    utterance.pitch = 1
    
    synth.speak(utterance)
    toast.success("🔊 播放中...", { duration: 1000 })
  }

  // 生成差異化顯示 HTML
  const getDiffDisplay = (correct: string, input: string) => {
    const correctChars = correct.split("")
    const inputChars = input.split("")
    
    const maxLen = Math.max(correctChars.length, inputChars.length)
    
    const correctDisplay: JSX.Element[] = []
    const inputDisplay: JSX.Element[] = []
    
    for (let i = 0; i < maxLen; i++) {
      const correctChar = correctChars[i] || "_"
      const inputChar = inputChars[i] || "_"
      
      const isMatch = correctChar === inputChar && correctChar !== "_"
      const bgColor = isMatch ? "bg-green-500" : correctChar === "_" ? "bg-gray-300" : "bg-red-500"
      const textColor = correctChar === "_" ? "text-gray-300" : "text-white"
      
      correctDisplay.push(
        <span
          key={`c-${i}`}
          className={`inline-flex items-center justify-center w-9 h-11 m-0.5 rounded-lg ${bgColor} ${textColor} font-bold text-2xl`}
        >
          {correctChar}
        </span>
      )
      
      const inputBgColor = isMatch ? "bg-green-500" : inputChar === "_" ? "bg-gray-300" : "bg-red-500"
      const inputTextColor = inputChar === "_" ? "text-gray-300" : "text-white"
      
      inputDisplay.push(
        <span
          key={`i-${i}`}
          className={`inline-flex items-center justify-center w-9 h-11 m-0.5 rounded-lg ${inputBgColor} ${inputTextColor} font-bold text-2xl`}
        >
          {inputChar}
        </span>
      )
    }
    
    return (
      <div className="my-4">
        <div className="mb-2">{correctDisplay}</div>
        <div className="text-gray-500 text-sm my-2">⬇️</div>
        <div>{inputDisplay}</div>
      </div>
    )
  }

  // 進入下一題
  const goNextQuestion = () => {
    if (studyMode === "REVIEW") {
      if (wrongQueue.length > 0) {
        const nextIdx = wrongQueue[0]
        setCurrentDisplayIndex(nextIdx)
      } else {
        setStudyMode("LEARNING")
        setSequenceCursor(0)
        setCurrentDisplayIndex(0)
        toast.success("🎉 錯題複習完畢！開始新的一輪！", { duration: 3000 })
      }
    } else if (studyMode === "LEARNING") {
      const nextCursor = sequenceCursor + 1
      
      if (nextCursor < chineseWords.length) {
        setSequenceCursor(nextCursor)
        setCurrentDisplayIndex(nextCursor)
      } else {
        if (wrongQueue.length > 0) {
          setStudyMode("REVIEW")
          toast("🔄 一輪結束，進入錯題複習模式！", {
            icon: "🔥",
            duration: 3000
          })
          setCurrentDisplayIndex(wrongQueue[0])
        } else {
          setSequenceCursor(0)
          setCurrentDisplayIndex(0)
          toast.success("💯 太強了！全部答對，直接開始新的一輪！", { duration: 3000 })
        }
      }
    }
  }

  // 提交答案
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    const trimmedInput = userInput.trim()
    const isCorrect = trimmedInput === currentWord
    
    // 更新統計
    const newStats = [...stats]
    if (isCorrect) {
      newStats[currentDisplayIndex].correct += 1
    } else {
      newStats[currentDisplayIndex].wrong += 1
    }
    setStats(newStats)
    
    // 更新錯題隊列
    if (isCorrect) {
      if (wrongQueue.includes(currentDisplayIndex)) {
        setWrongQueue(wrongQueue.filter(idx => idx !== currentDisplayIndex))
      }
    } else {
      if (!wrongQueue.includes(currentDisplayIndex)) {
        setWrongQueue([...wrongQueue, currentDisplayIndex])
      } else if (studyMode === "REVIEW" && wrongQueue[0] === currentDisplayIndex) {
        const newQueue = [...wrongQueue]
        const item = newQueue.shift()
        if (item !== undefined) {
          newQueue.push(item)
        }
        setWrongQueue(newQueue)
      }
    }
    
    // 添加歷史記錄
    const now = new Date().toLocaleString("zh-TW")
    setHistory([
      {
        mode: studyMode === "REVIEW" ? "複習" : "一般",
        questionNumber: currentDisplayIndex + 1,
        word: currentWord,
        input: trimmedInput,
        result: isCorrect ? "正確" : "錯誤",
        time: now
      },
      ...history
    ])
    
    // 顯示結果
    setLastResult({
      isCorrect,
      diff: trimmedInput
    })
    setShowResult(true)
    
    // 播放音效提示
    if (isCorrect) {
      playSound("correct")
      toast.success("✅ 答對了！太棒了！", { duration: 2000 })
    } else {
      playSound("wrong")
      toast.error(`❌ ${trimmedInput ? "答錯了" : "跳過"}！正確答案是：${currentWord}`, {
        duration: 3000
      })
    }
  }

  // 下一題
  const handleNext = () => {
    setShowResult(false)
    setLastResult(null)
    setUserInput("")
    goNextQuestion()
  }

  // 跳過
  const handleSkip = () => {
    setUserInput("")
    const form = document.querySelector("form")
    if (form) {
      form.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }))
    }
  }

  // 計算總體統計
  const totalCorrect = stats.reduce((sum, s) => sum + s.correct, 0)
  const totalWrong = stats.reduce((sum, s) => sum + s.wrong, 0)
  const totalTries = totalCorrect + totalWrong
  const accuracy = totalTries > 0 ? ((totalCorrect / totalTries) * 100).toFixed(1) : "0.0"

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Toaster position="top-center" />
      
      {/* 側邊欄 */}
      <div
        className={`fixed top-0 left-0 h-full bg-white border-r border-gray-200 transition-transform duration-300 z-50 ${
          showSidebar ? "translate-x-0" : "-translate-x-full"
        } w-80 overflow-y-auto`}
      >
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-blue-500">📊 學習統計</h2>
            <button
              onClick={() => setShowSidebar(false)}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
          </div>
          
          {/* 學習模式狀態 */}
          <div className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-2xl p-4 mb-6 shadow-lg">
            <div className="flex items-center gap-2 mb-2">
              <BookOpen className="w-5 h-5" />
              <span className="font-bold">學習模式</span>
            </div>
            <div className="text-2xl font-bold mb-1">{studyMode === "LEARNING" ? "一般學習" : "錯題複習"}</div>
            <div className="text-sm opacity-90">待複習題數：{wrongQueue.length}</div>
          </div>

          {/* 總體統計 */}
          <div className="bg-white rounded-2xl border-2 border-gray-100 p-4 mb-6">
            <div className="flex justify-between mb-3">
              <div>
                <div className="text-sm text-gray-500">答對</div>
                <div className="text-2xl font-bold text-green-500">{totalCorrect}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">答錯</div>
                <div className="text-2xl font-bold text-red-500">{totalWrong}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">正確率</div>
                <div className="text-2xl font-bold text-blue-500">{accuracy}%</div>
              </div>
            </div>
          </div>
          
          {/* 詞彙統計 */}
          <div className="mb-6">
            <h3 className="text-lg font-bold text-gray-700 mb-3 flex items-center gap-2">
              <Target className="w-5 h-5" />
              詞彙統計
            </h3>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {chineseWords.map((word, idx) => {
                const s = stats[idx]
                const tries = s.correct + s.wrong
                const rate = tries > 0 ? `${s.correct}/${tries}` : "0/0"
                
                let statusLight = "⚪"
                if (wrongQueue.includes(idx)) {
                  statusLight = "🔴"
                } else if (s.correct > 0) {
                  statusLight = "🟢"
                } else if (s.wrong > 0) {
                  statusLight = "🟡"
                }
                
                return (
                  <div
                    key={idx}
                    className={`flex items-center justify-between p-3 rounded-lg ${
                      idx === currentDisplayIndex
                        ? "bg-blue-50 border-2 border-blue-300"
                        : "bg-gray-50 border border-gray-200"
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span>{statusLight}</span>
                      <span className="font-medium text-gray-700">{idx + 1}. {word}</span>
                    </div>
                    <span className="text-sm font-semibold text-gray-600">{rate}</span>
                  </div>
                )
              })}
            </div>
          </div>
          
          {/* 歷史記錄 */}
          <div>
            <h3 className="text-lg font-bold text-gray-700 mb-3">📝 歷史記錄</h3>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {history.slice(0, 20).map((item, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-lg text-sm ${
                    item.result === "正確"
                      ? "bg-green-50 border border-green-200"
                      : "bg-red-50 border border-red-200"
                  }`}
                >
                  <div className="flex justify-between mb-1">
                    <span className="font-bold">{item.word}</span>
                    <span className={item.result === "正確" ? "text-green-600" : "text-red-600"}>
                      {item.result}
                    </span>
                  </div>
                  <div className="text-gray-600">輸入：{item.input || "(空白)"}</div>
                  <div className="text-gray-400 text-xs mt-1">{item.time}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {/* 主內容區 */}
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-2xl">
          {/* 標題和統計按鈕 */}
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-cyan-500">
              🎧 中文詞彙聽力練習
            </h1>
            <button
              onClick={() => setShowSidebar(true)}
              className="bg-white hover:bg-gray-50 text-gray-700 p-3 rounded-xl shadow-lg transition-all"
            >
              <BarChart3 className="w-6 h-6" />
            </button>
          </div>

          {/* 模式提示 */}
          {studyMode === "REVIEW" && (
            <div className="bg-gradient-to-r from-orange-500 to-yellow-500 text-white rounded-2xl p-4 mb-6 shadow-lg">
              <div className="flex items-center gap-2 font-bold text-lg">
                🔥 錯題複習模式 (剩餘 {wrongQueue.length} 題)
              </div>
            </div>
          )}

          {/* 主卡片 */}
          <div className="bg-white rounded-3xl shadow-2xl p-8">
            {/* 貓頭鷹和播放按鈕 */}
            <div className="flex items-center gap-4 mb-8">
              <div className="text-6xl animate-bounce">🦉</div>
              <button
                onClick={() => playTTS(currentWord)}
                className="flex-1 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-bold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105 flex items-center justify-center gap-3"
              >
                <Volume2 className="w-6 h-6" />
                <span className="text-xl">播放詞彙發音</span>
              </button>
            </div>

            {/* 結果顯示 */}
            {showResult && lastResult && (
              <div className={`mb-6 p-6 rounded-2xl ${
                lastResult.isCorrect
                  ? "bg-gradient-to-r from-green-500 to-green-600"
                  : "bg-white border-2 border-gray-200"
              }`}>
                <div className={`font-bold text-xl mb-2 ${
                  lastResult.isCorrect ? "text-white" : "text-gray-700"
                }`}>
                  {lastResult.isCorrect ? "✅ 答對了！太棒了！" : `❌ ${lastResult.diff ? "答錯了" : "跳過"}！正確答案是：${currentWord}`}
                </div>
                
                {!lastResult.isCorrect && getDiffDisplay(currentWord, lastResult.diff)}
              </div>
            )}

            {/* 答題表單 */}
            {!showResult && (
              <form onSubmit={handleSubmit} className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  ✏️ 請輸入你聽到的中文詞彙
                </label>
                <input
                  ref={inputRef}
                  type="text"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  placeholder="在此輸入..."
                  className="w-full px-6 py-4 text-xl border-2 border-gray-300 rounded-2xl focus:border-blue-500 focus:ring-4 focus:ring-blue-200 transition-all outline-none"
                  autoComplete="off"
                />
              </form>
            )}

            {/* 按鈕組 */}
            <div className="flex gap-3">
              {!showResult ? (
                <>
                  <button
                    onClick={handleSubmit}
                    className="flex-1 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-bold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
                  >
                    提交答案
                  </button>
                  <button
                    onClick={handleSkip}
                    className="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold py-4 px-6 rounded-2xl transition-all flex items-center gap-2"
                  >
                    <SkipForward className="w-5 h-5" />
                    跳過
                  </button>
                </>
              ) : (
                <button
                  onClick={handleNext}
                  className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-bold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
                >
                  下一題
                </button>
              )}
            </div>

            {/* 進度顯示 */}
            <div className="mt-6 text-center text-gray-500 text-sm">
              <p>題目 {currentDisplayIndex + 1} / {chineseWords.length}</p>
              <p className="mt-2">💡 小提示：按 Enter 鍵可以快速提交答案</p>
            </div>
          </div>
        </div>
      </div>

      {/* 遮罩層 */}
      {showSidebar && (
        <div
          className="fixed inset-0 bg-black bg-opacity-30 z-40"
          onClick={() => setShowSidebar(false)}
        />
      )}
    </div>
  )
}

export default App
