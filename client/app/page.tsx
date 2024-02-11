'use client'
import React, { useState, useEffect, useRef } from 'react'
import ChatBubble from '@/components/component/chat-bubble'
import { ChatForm } from '@/components/component/chat-form'
import BotTyping from '@/components/ui/bot-typing'
import Sidebar from '@/components/component/sidebar'
import Loading from '@/components/ui/loading'
import { v4 as uuidv4 } from 'uuid'
import { signOut, useSession } from 'next-auth/react'
import { redirect } from 'next/navigation'
import { Message, ChatHistory } from '@/lib/types'

export default function Home() {
  const [isBotTyping, setIsBotTyping] = useState(false)
  const [data, setData] = useState<Message[]>([])
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([])
  const [isNewChat, setIsNewChat] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement | null>(null)

  const { data: session, status } = useSession({
    required: true,
    onUnauthenticated() {
      redirect('/auth/signin')
    },
  })

  const handleFormSubmit = (message: Message) => {
    setData((prev) => {
      const newData = [...prev, message]
      if (chatHistory.length > 0 && !isNewChat) {
        // Create a new copy of the last chat history item and update it with the new data
        const lastChatHistory = { ...chatHistory[chatHistory.length - 1] }
        lastChatHistory.messages = newData
        setChatHistory([...chatHistory.slice(0, -1), lastChatHistory])
      } else {
        // If there's no chat history or a new chat is started, create a new one
        setChatHistory([...chatHistory, { id: uuidv4(), messages: newData }])
        setIsNewChat(false) // Reset the new chat flag
      }
      return newData
    })
  }

  const handleClearChat = () => {
    setData([])
    setIsNewChat(true)
  }

  const handleRemoveChatHistory = (id: string) => {
    setChatHistory(chatHistory.filter((history) => history.id !== id))
    setData([])
  }

  const handleSidebarItemClick = (id: string) => {
    setData([])
    setIsNewChat(false)
    const history = chatHistory.find((history) => history.id === id)
    if (history) {
      // Use a timeout to allow the chat to clear before setting the data
      setTimeout(() => {
        setData(history.messages)
      }, 0)
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
