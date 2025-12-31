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

  // --- 語音相關修正 ---
  const synth = typeof window !== "undefined" ? window.speechSynthesis : null
  const voicesRef = useRef<SpeechSynthesisVoice[]>([])

  // 音效 Audio 元素
  const correctSound = useRef<HTMLAudioElement | null>(null)
  const wrongSound = useRef<HTMLAudioElement | null>(null)

  const currentWord = chineseWords[currentDisplayIndex]

  // 初始化音效與語音引擎
  useEffect(() => {
    correctSound.current = new Audio("https://static.lumi.new/material/f5/f5901670ee5c4ee9a934c52a076ee945.mp3")
    wrongSound.current = new Audio("https://static.lumi.new/material/d5/d59fce81a6ec4629dca550ecc81a4892.mp3")

    const loadVoices = () => {
      if (synth) {
        const availableVoices = synth.getVoices()
        voicesRef.current = availableVoices
        console.log("語音清單已加載:", availableVoices.length)
      }
    }

    loadVoices()
    if (synth && synth.onvoiceschanged !== undefined) {
      synth.onvoiceschanged = loadVoices
    }
  }, [synth])

  // 播放音效
  const playSound = (type: "correct" | "wrong") => {
    if (type === "correct" && correctSound.current) {
      correctSound.current.currentTime = 0
      correctSound.current.play().catch(e => console.log("音效播放失敗:", e))
    } else if (type === "wrong" && wrongSound.current) {
      wrongSound.current.currentTime = 0
      wrongSound.current.play().catch(e => console.log("音效播放失敗:", e))
      setTimeout(() => {
        if (wrongSound.current) {
          wrongSound.current.pause()
          wrongSound.current.currentTime = 0
        }
      }, 1000)
    }
  }

  // 語音播放核心邏輯
  const startSpeech = (text: string) => {
    if (!synth) return

    // 解決部分平板瀏覽器卡住的問題
    synth.cancel()
    synth.resume()

    const voices = voicesRef.current.length > 0 ? voicesRef.current : synth.getVoices()
    const utterance = new SpeechSynthesisUtterance(text)

    // 精確尋找中文語音
    const chineseVoice =
      voices.find(v => v.lang === 'zh-TW') ||
      voices.find(v => v.lang === 'zh-HK') ||
      voices.find(v => v.lang.startsWith('zh'))

    if (chineseVoice) {
      utterance.voice = chineseVoice
      utterance.lang = chineseVoice.lang
    } else {
      utterance.lang = "zh-TW"
    }

    utterance.rate = 0.8
    utterance.pitch = 1.0
    utterance.volume = 1.0

    utterance.onstart = () => toast.success("🔊 播放中...", { id: "playing-toast", duration: 1000 })

    synth.speak(utterance)
  }

  const playTTS = (text: string) => {
    try {
      if (!synth) {
        toast.error("❌ 語音功能不可用")
        return
      }
      startSpeech(text)
    } catch (error) {
      console.error("語音播放錯誤:", error)
    }
  }

  // 自動聚焦
  useEffect(() => {
    if (!showResult && inputRef.current) {
      inputRef.current.focus()
    }
  }, [currentDisplayIndex, showResult])

  // --- 其餘邏輯保持不變 ---
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
      correctDisplay.push(
        <span key={`c-${i}`} className={`inline-flex items-center justify-center w-9 h-11 m-0.5 rounded-lg ${bgColor} text-white font-bold text-2xl`}>
          {correctChar}
        </span>
      )
      const inputBgColor = isMatch ? "bg-green-500" : inputChar === "_" ? "bg-gray-300" : "bg-red-500"
      inputDisplay.push(
        <span key={`i-${i}`} className={`inline-flex items-center justify-center w-9 h-11 m-0.5 rounded-lg ${inputBgColor} text-white font-bold text-2xl`}>
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

  const goNextQuestion = () => {
    if (studyMode === "REVIEW") {
      if (wrongQueue.length > 0) {
        setCurrentDisplayIndex(wrongQueue[0])
      } else {
        setStudyMode("LEARNING")
        setSequenceCursor(0)
        setCurrentDisplayIndex(0)
        toast.success("🎉 錯題複習完畢！")
      }
    } else {
      const nextCursor = sequenceCursor + 1
      if (nextCursor < chineseWords.length) {
        setSequenceCursor(nextCursor)
        setCurrentDisplayIndex(nextCursor)
      } else {
        if (wrongQueue.length > 0) {
          setStudyMode("REVIEW")
          setCurrentDisplayIndex(wrongQueue[0])
        } else {
          setSequenceCursor(0)
          setCurrentDisplayIndex(0)
        }
      }
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const trimmedInput = userInput.trim()
    const isCorrect = trimmedInput === currentWord
    const newStats = [...stats]
    if (isCorrect) newStats[currentDisplayIndex].correct += 1
    else newStats[currentDisplayIndex].wrong += 1
    setStats(newStats)

    if (isCorrect) {
      setWrongQueue(wrongQueue.filter(idx => idx !== currentDisplayIndex))
    } else {
      if (!wrongQueue.includes(currentDisplayIndex)) {
        setWrongQueue([...wrongQueue, currentDisplayIndex])
      }
    }

    setHistory([{
      mode: studyMode === "REVIEW" ? "複習" : "一般",
      questionNumber: currentDisplayIndex + 1,
      word: currentWord,
      input: trimmedInput,
      result: isCorrect ? "正確" : "錯誤",
      time: new Date().toLocaleString()
    }, ...history])

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

  const totalCorrect = stats.reduce((sum, s) => sum + s.correct, 0)
  const totalWrong = stats.reduce((sum, s) => sum + s.wrong, 0)
  const accuracy = (totalCorrect + totalWrong) > 0 ? ((totalCorrect / (totalCorrect + totalWrong)) * 100).toFixed(1) : "0.0"

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Toaster position="top-center" />

      {/* 側邊欄 (省略重複部分以保持簡潔，邏輯同原版) */}
      <div className={`fixed top-0 left-0 h-full bg-white border-r transition-transform z-50 ${showSidebar ? "translate-x-0" : "-translate-x-full"} w-80 overflow-y-auto`}>
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-blue-500">📊 學習統計</h2>
            <button onClick={() => setShowSidebar(false)} className="text-gray-500 text-2xl">×</button>
          </div>
          <div className="bg-blue-500 text-white rounded-2xl p-4 mb-6 shadow-lg">
            <div className="font-bold">模式：{studyMode === "LEARNING" ? "一般學習" : "錯題複習"}</div>
            <div className="text-sm">正確率：{accuracy}%</div>
          </div>
          <div className="space-y-2">
            {chineseWords.map((word, idx) => (
              <div key={idx} className={`p-2 rounded border ${idx === currentDisplayIndex ? "bg-blue-50 border-blue-300" : "bg-white"}`}>
                {idx + 1}. {word} (對:{stats[idx].correct} 錯:{stats[idx].wrong})
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-2xl">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold text-blue-600">🎧 中文詞彙聽力練習</h1>
            <button onClick={() => setShowSidebar(true)} className="p-3 bg-white rounded-xl shadow-md"><BarChart3 /></button>
          </div>

          <div className="bg-gray-900 rounded-3xl shadow-2xl p-8 border-4 border-yellow-500">
            <div className="flex items-center gap-4 mb-8">
              <div className="text-6xl animate-bounce">🦉</div>
              <button
                onClick={() => playTTS(currentWord)}
                className="flex-1 bg-green-500 hover:bg-green-600 text-white font-bold py-4 rounded-2xl shadow-lg flex items-center justify-center gap-3 transition-transform active:scale-95"
              >
                <Volume2 className="w-6 h-6" />
                <span className="text-xl">播放詞彙發音</span>
              </button>
            </div>

            {showResult && lastResult ? (
              <div className="mb-6 p-6 rounded-2xl bg-white">
                <div className={`font-bold text-xl mb-2 ${lastResult.isCorrect ? "text-green-600" : "text-red-600"}`}>
                  {lastResult.isCorrect ? "✅ 答對了！" : `❌ 正確答案：${currentWord}`}
                </div>
                {!lastResult.isCorrect && getDiffDisplay(currentWord, lastResult.diff)}
                <button onClick={handleNext} className="w-full bg-blue-500 text-white font-bold py-4 rounded-2xl mt-4">下一題</button>
              </div>
            ) : (
              <form onSubmit={handleSubmit}>
                <label className="block text-yellow-500 mb-2 font-bold">✏️ 請輸入詞彙：</label>
                <input
                  ref={inputRef}
                  type="text"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  className="w-full px-6 py-4 text-2xl bg-gray-800 text-yellow-400 border-2 border-yellow-500 rounded-2xl outline-none"
                  autoComplete="off"
                />
                <div className="flex gap-4 mt-6">
                  <button type="submit" className="flex-1 bg-green-500 text-white font-bold py-4 rounded-2xl">提交答案</button>
                  <button type="button" onClick={handleNext} className="bg-gray-700 text-white px-6 rounded-2xl"><SkipForward /></button>
                </div>
              </form>
            )}
            <div className="mt-6 text-center text-yellow-600">題目 {currentDisplayIndex + 1} / {chineseWords.length}</div>
          </div>
        </div>
      </div>
      {showSidebar && <div className="fixed inset-0 bg-black/30 z-40" onClick={() => setShowSidebar(false)} />}
    </div>
  )
}

export default App
