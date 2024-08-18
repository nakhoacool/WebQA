'use client'
import React, {
  createContext,
  useState,
  useRef,
  useEffect,
  Dispatch,
  SetStateAction,
  MutableRefObject,
} from 'react'
import { Message, ChatHistory } from '@/lib/types'
import { v4 as uuidv4 } from 'uuid'

type ChatContextType = {
  isBotTyping: boolean
  setIsBotTyping: Dispatch<SetStateAction<boolean>>
  data: Message[]
  setData: Dispatch<SetStateAction<Message[]>>
  chatHistory: ChatHistory[]
  setChatHistory: Dispatch<SetStateAction<ChatHistory[]>>
  isNewChat: boolean
  setIsNewChat: Dispatch<SetStateAction<boolean>>
  activeChatHistoryId: string | null
  setActiveChatHistoryId: Dispatch<SetStateAction<string | null>>
  abortController: AbortController | null
  setAbortController: Dispatch<SetStateAction<AbortController | null>>
  messagesEndRef: MutableRefObject<HTMLDivElement>
  handleFormSubmit: (message: Message) => void
  handleClearChat: () => void
  handleRemoveChatHistory: (id: string) => void
  handleSidebarItemClick: (id: string) => void
  selectedOption: string
  setSelectedOption: Dispatch<SetStateAction<string>>
  setUserID: Dispatch<SetStateAction<string | null>>
}

export const ChatContext = createContext<ChatContextType | undefined>(undefined)

export const ChatProvider = ({ children }: { children: React.ReactNode }) => {
  const [isBotTyping, setIsBotTyping] = useState(false)
  const [data, setData] = useState<Message[]>([])
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([])
  const [isNewChat, setIsNewChat] = useState(true)
  const [activeChatHistoryId, setActiveChatHistoryId] = useState<string | null>(
    null
  )
  const [abortController, setAbortController] =
    useState<AbortController | null>(null)
  const [selectedOption, setSelectedOption] = useState('tdt')
  const messagesEndRef = useRef<HTMLDivElement>(null!)
  const [userID, setUserID] = useState<string | null>(null)

  useEffect(() => {
    const savedChatHistory = localStorage.getItem(`chatHistory_${userID}`)
    if (savedChatHistory) {
      setChatHistory(JSON.parse(savedChatHistory))
    }
  }, [userID])

  useEffect(() => {
    localStorage.setItem(`chatHistory_${userID}`, JSON.stringify(chatHistory))
  }, [chatHistory, userID])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [data])

  const handleFormSubmit = (message: Message) => {
    setData((prev) => {
      const newData = [...prev, message]
      if (chatHistory.length > 0 && !isNewChat && activeChatHistoryId) {
        const activeChatHistoryIndex = chatHistory.findIndex(
          (history) => history.id === activeChatHistoryId
        )
        if (activeChatHistoryIndex !== -1) {
          const activeChatHistory = { ...chatHistory[activeChatHistoryIndex] }
          activeChatHistory.messages = newData
          setChatHistory([
            ...chatHistory.slice(0, activeChatHistoryIndex),
            activeChatHistory,
            ...chatHistory.slice(activeChatHistoryIndex + 1),
          ])
        }
      } else {
        // If there's no chat history or a new chat is started, create a new one
        const date = new Date()
        const dateString = `${date.getFullYear()}-${
          date.getMonth() + 1
        }-${date.getDate()}-${date.getHours()}-${date.getMinutes()}-${date.getSeconds()}`
        const newChatHistoryId = uuidv4()
        setActiveChatHistoryId(newChatHistoryId)
        setChatHistory([
          ...chatHistory,
          {
            id: newChatHistoryId,
            title: `Chat ${dateString}`,
            uniOption: selectedOption,
            messages: newData,
          },
        ])
        setIsNewChat(false) // Reset the new chat flag
      }
      return newData
    })
  }

  const handleClearChat = () => {
    if (abortController) {
      abortController.abort()
      setAbortController(null)
    }
    setData([])
    setIsNewChat(true)
    setActiveChatHistoryId(null)
    setIsBotTyping(false)
  }

  const handleRemoveChatHistory = (id: string) => {
    setChatHistory(chatHistory.filter((history) => history.id !== id))
    setData([])
  }

  const handleSidebarItemClick = (id: string) => {
    if (abortController) {
      abortController.abort()
      setAbortController(null)
    }
    setData([])
    setIsNewChat(false)
    setActiveChatHistoryId(id)
    setIsBotTyping(false)
    setSelectedOption(
      chatHistory.find((history) => history.id === id)?.uniOption || 'tdt'
    )
    const history = chatHistory.find((history) => history.id === id)
    if (history) {
      setData(history.messages)
    }
  }

  return (
    <ChatContext.Provider
      value={{
        isBotTyping,
        setIsBotTyping,
        data,
        setData,
        chatHistory,
        setChatHistory,
        isNewChat,
        setIsNewChat,
        activeChatHistoryId,
        setActiveChatHistoryId,
        abortController,
        setAbortController,
        messagesEndRef,
        handleFormSubmit,
        handleClearChat,
        handleRemoveChatHistory,
        handleSidebarItemClick,
        selectedOption,
        setSelectedOption,
        setUserID,
      }}
    >
      {children}
    </ChatContext.Provider>
  )
}
