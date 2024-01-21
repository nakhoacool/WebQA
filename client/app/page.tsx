'use client'
import { AvatarImage, AvatarFallback, Avatar } from '@/components/ui/avatar'
import ChatBubble from '@/components/ui/chat-bubble'
import { ChatForm } from '@/components/component/chat-form'
import React, { useState, useEffect, useRef } from 'react'
import BotTyping from '@/components/ui/bot-typing'
import PlusIcon from '@/components/icon/plus'
import TrashIcon from '@/components/icon/trash'
import { v4 as uuidv4 } from 'uuid'
interface Message {
  role: string
  content: string
}

interface ChatHistory {
  id: number
  messages: Message[]
}

export default function Home() {
  const [isBotTyping, setIsBotTyping] = useState(false)
  const [data, setData] = useState<Message[]>([])
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([])
  const messagesEndRef = useRef<HTMLDivElement | null>(null)
  const [isHovered, setIsHovered] = useState(false)

  const handleFormSubmit = (message: Message) => {
    setData((prev) => {
      const newData = [...prev, message]
      setChatHistory([...chatHistory, { id: uuidv4(), messages: newData }])
      return newData
    })
  }

  const handleClearChat = () => {
    setData([])
  }

  const handleRemove = (indexToRemove: number) => {
    setChatHistory(chatHistory.filter((_, index) => index !== indexToRemove))
    setData([])
  }

  const handleSidebarItemClick = (id: number) => {
    // Clear the chat
    setData([])

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

  return (
    <div className='flex h-screen bg-gray-800 text-white'>
      {/* Sidebar */}
      <div className='flex flex-col w-64 border-r border-gray-700'>
        <div className='px-4 py-2 flex items-center justify-between border-b border-gray-700'>
          <h2 className='text-lg font-semibold'>New chat</h2>
          <button
            className='p-2 rounded-full hover:bg-gray-600 focus:outline-none focus:ring hover:scale-105 transition-transform duration-200 ease-in-out'
            onClick={handleClearChat}
          >
            <PlusIcon className='text-white h-6 w-6' />
          </button>
        </div>
        <div className='overflow-y-auto'>
          {chatHistory.map((item, index) => (
            <div
              key={item.id}
              className='px-4 py-2 hover:bg-gray-700 cursor-pointer flex justify-between items-center'
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
              onClick={() => handleSidebarItemClick(item.id)}
            >
              <p className='w-40 text-sm truncate'>Chat {index}</p>
              {isHovered && (
                <TrashIcon
                  className='h-5 w-5'
                  onClick={(event) => {
                    event.stopPropagation()
                    handleRemove(item.id)
                  }}
                />
              )}
            </div>
          ))}
        </div>
        <div className='px-4 py-2 flex items-center space-x-2 border-t border-gray-700 mt-auto'>
          <Avatar>
            <AvatarImage
              alt='Guest'
              src='/placeholder.svg?height=32&width=32'
            />
            <AvatarFallback>G</AvatarFallback>
          </Avatar>
          <span className='text-sm'>Guest</span>
        </div>
      </div>
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
          />
        </div>
      </div>
    </div>
  )
}
