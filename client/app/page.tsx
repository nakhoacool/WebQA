'use client'
import React, { useState, useEffect, useRef } from 'react'
import ChatBubble from '@/components/component/chat-bubble'
import { ChatForm } from '@/components/component/chat-form'
import BotTyping from '@/components/ui/bot-typing'
import Sidebar from '@/components/component/sidebar'
import Loading from '@/components/ui/loading'
import { v4 as uuidv4 } from 'uuid'
import { useSession } from 'next-auth/react'
import { redirect } from 'next/navigation'
import { Message, ChatHistory } from '@/lib/types'

export default function Home() {
  const [isBotTyping, setIsBotTyping] = useState(false)
  const [data, setData] = useState<Message[]>([])
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([])
  const [isNewChat, setIsNewChat] = useState(false)
  const [activeChatHistoryId, setActiveChatHistoryId] = useState<string | null>(
    null
  )
  const messagesEndRef = useRef<HTMLDivElement | null>(null)

  const { data: session, status } = useSession({
    required: true,
    onUnauthenticated() {
      redirect('/auth/signin')
    },
  })

  const date = new Date()
  const dateString = `${date.getFullYear()}-${
    date.getMonth() + 1
  }-${date.getDate()}-${date.getHours()}-${date.getMinutes()}-${date.getSeconds()}`

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
        const newChatHistoryId = uuidv4()
        setActiveChatHistoryId(newChatHistoryId)
        setChatHistory([
          ...chatHistory,
          {
            id: newChatHistoryId,
            title: `Chat ${dateString}`,
            messages: newData,
          },
        ])
        setIsNewChat(false) // Reset the new chat flag
      }
      return newData
    })
  }

  const handleClearChat = () => {
    setData([])
    setIsNewChat(true)
    setActiveChatHistoryId(null)
  }

  const handleRemoveChatHistory = (id: string) => {
    setChatHistory(chatHistory.filter((history) => history.id !== id))
    setData([])
  }

  const handleSidebarItemClick = (id: string) => {
    setData([])
    setIsNewChat(false)
    setActiveChatHistoryId(id)
    const history = chatHistory.find((history) => history.id === id)
    if (history) {
      setData(history.messages)
    }
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [data])

  if (status === 'loading') {
    return <Loading />
  }

  return (
    <div className='flex h-screen bg-gray-800 text-white'>
      {/* Sidebar */}
      <Sidebar
        session={session}
        chatHistory={chatHistory}
        handleClearChat={handleClearChat}
        handleSidebarItemClick={handleSidebarItemClick}
        handleRemoveChatHistory={handleRemoveChatHistory}
        activeChatHistoryId={activeChatHistoryId}
      />
      {/* Chat */}
      <div className='flex-1 flex flex-col'>
        {/* Chat message */}
        <div className='flex-1 overflow-y-auto'>
          {data.map((data, index) => (
            <ChatBubble key={index} data={data} />
          ))}
          {isBotTyping && <BotTyping />}
          {/* Scroll to bottom */}
          <div ref={messagesEndRef} />
        </div>
        {/* Chat form */}
        <div className='flex items-center'>
          <ChatForm
            onSubmit={handleFormSubmit}
            setIsTyping={setIsBotTyping}
            isTyping={isBotTyping}
            chatHistory={data}
          />
        </div>
      </div>
    </div>
  )
}

Home.requireAuth = true
