import { useState, useRef, useEffect } from 'react'

const suggestions = [
  'What are Fundamental Rights?',
  'Explain Article 21',
  'What is the Preamble?',
]

function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Namaste. I am ConstitutionGPT, ready to help you explore the Indian Constitution.' }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  // Auto-scroll to the newest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage = { role: 'user', content: input }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const history = messages
        .slice(1)
        .filter((msg) => msg.role === 'user' || msg.role === 'assistant')
        .map((msg) => ({ role: msg.role, content: msg.content }))

      const response = await fetch('http://127.0.0.1:5001/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMessage.content, history }),
      })

      const data = await response.json()
      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Network response was not ok')
      }

      setMessages((prev) => [...prev, { role: 'assistant', content: data.answer }])
    } catch (error) {
      console.error("Error fetching response:", error)
      setMessages((prev) => [
        ...prev, 
        { role: 'assistant', content: `Error: ${error.message}` }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex h-screen flex-col bg-[#f8f5ef] font-sans text-slate-950">
      <header className="border-b border-orange-200/70 bg-white shadow-sm">
        <div className="h-1.5 bg-gradient-to-r from-[#ff9933] via-white to-[#138808]" />
        <div className="mx-auto flex w-full max-w-5xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
          <div className="flex min-w-0 items-center gap-3">
            <img
              src="/indian-flag.svg"
              alt="Indian flag"
              className="h-16 w-16 shrink-0 object-contain"
            />
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[#b35a00]">Indian Constitution</p>
              <h1 className="truncate text-2xl font-bold tracking-wide text-slate-950">ConstitutionGPT</h1>
            </div>
          </div>
          <div className="hidden items-center gap-2 rounded-full border border-green-200 bg-green-50 px-3 py-1.5 text-sm font-medium text-green-800 sm:flex">
            <span className="h-2 w-2 rounded-full bg-[#138808]" />
            Satyameva Jayate
          </div>
        </div>
      </header>

      <section className="border-b border-orange-100 bg-gradient-to-r from-orange-50 via-white to-green-50">
        <div className="mx-auto grid w-full max-w-5xl gap-4 px-4 py-5 sm:px-6 lg:grid-cols-[1.25fr_0.75fr]">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#0b3d91]">Justice, Liberty, Equality, Fraternity</p>
            <h2 className="mt-2 text-2xl font-bold text-slate-950 sm:text-3xl">Ask questions grounded in the Constitution of India.</h2>
          </div>
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="border-b-4 border-[#ff9933] bg-white px-3 py-3 shadow-sm">
              <p className="text-lg font-bold text-slate-950">395</p>
              <p className="text-xs text-slate-600">Articles</p>
            </div>
            <div className="border-b-4 border-[#0b3d91] bg-white px-3 py-3 shadow-sm">
              <p className="text-lg font-bold text-slate-950">22</p>
              <p className="text-xs text-slate-600">Parts</p>
            </div>
            <div className="border-b-4 border-[#138808] bg-white px-3 py-3 shadow-sm">
              <p className="text-lg font-bold text-slate-950">1950</p>
              <p className="text-xs text-slate-600">In force</p>
            </div>
          </div>
        </div>
      </section>

      <main className="mx-auto w-full max-w-5xl flex-1 overflow-y-auto p-4 sm:p-6">
        <div className="mb-5 flex flex-wrap gap-2">
          {suggestions.map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              onClick={() => setInput(suggestion)}
              className="border border-orange-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:border-[#ff9933] hover:text-slate-950"
            >
              {suggestion}
            </button>
          ))}
        </div>
        <div className="flex flex-col space-y-6">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[88%] p-4 shadow-sm sm:max-w-[75%] ${
                  msg.role === 'user'
                    ? 'bg-[#0b3d91] text-white'
                    : 'border border-orange-100 bg-white text-slate-900'
                }`}
              >
                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex items-center space-x-2 border border-orange-100 bg-white p-4 shadow-sm">
                <div className="h-2 w-2 animate-bounce rounded-full bg-[#ff9933]"></div>
                <div className="h-2 w-2 animate-bounce rounded-full bg-[#0b3d91] delay-100"></div>
                <div className="h-2 w-2 animate-bounce rounded-full bg-[#138808] delay-200"></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      <footer className="border-t border-orange-200/70 bg-white p-4">
        <div className="mx-auto w-full max-w-5xl">
          <form onSubmit={handleSend} className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about Fundamental Rights, Directive Principles, Articles, or Amendments..."
              className="flex-1 border border-orange-200 px-4 py-3 shadow-sm transition-all focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[#0b3d91]"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="bg-[#138808] px-6 py-3 font-semibold text-white shadow-sm transition-colors hover:bg-[#0f6d06] disabled:cursor-not-allowed disabled:opacity-50"
            >
              Send
            </button>
          </form>
        </div>
      </footer>
    </div>
  )
}

export default App
