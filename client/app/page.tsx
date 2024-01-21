'use client'
import { Sidebar } from '@/components/component/sidebar'
import ChatBubble from '@/components/ui/chat-bubble'
import { ChatForm } from '@/components/component/chat-form'
import React, { useState, useEffect, useRef, useReducer } from 'react'
import RobotIcon from '@/components/icon/robot'
interface Message {
  id: string
  role: string
  content: string
}

type Action = { type: 'add_message'; message: Message } | { type: 'clear_chat' }

const chatReducer = (state: Message[], action: Action) => {
  switch (action.type) {
    case 'add_message':
      return [...state, action.message]
    case 'clear_chat':
      return []
    default:
      return state
  }
}

export default function Home() {
  const [isBotTyping, setIsBotTyping] = useState(false)
  const [data, dispatch] = useReducer(chatReducer, [])
  const messagesEndRef = useRef<HTMLDivElement | null>(null)

  const handleFormSubmit = (message: Message) => {
    dispatch({ type: 'add_message', message })
  }

  const handleClearChat = () => {
    dispatch({ type: 'clear_chat' })
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [data])

  return (
    <div className='flex h-screen bg-gray-800 text-white'>
      {/* Sidebar */}
      <Sidebar onClearChat={handleClearChat} />
      {/* Chat */}
      <div className='flex-1 flex flex-col'>
        {/* Chat message */}
        <div className='flex-1 overflow-y-auto'>
          {data.map((data, index) => (
            <ChatBubble key={index} data={data} />
          ))}
          {isBotTyping && (
            <div className='p-4 flex'>
              <div className='rounded-full h-8 w-8 flex items-center justify-center mr-2'>
                <RobotIcon />
              </div>
              <div className='rounded-lg bg-gray-700 px-4 py-2 inline-block max-w-xs text-sm'>
                <div className='animate-pulse bg-gray-500 rounded-full h-2 w-2 mr-1 inline-block'></div>
                <div className='animate-pulse bg-gray-500 rounded-full h-2 w-2 mr-1 inline-block'></div>
                <div className='animate-pulse bg-gray-500 rounded-full h-2 w-2 inline-block'></div>
              </div>
            </div>
          )}
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
