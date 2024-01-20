'use client'
import { Sidebar } from '@/components/component/sidebar'
import ChatBubble from '@/components/ui/chat-bubble'
import { ChatForm } from '@/components/component/chat-form'
import React, { useState, useEffect, useRef } from 'react'

const testData = [
  { id: 'first chat', role: 'bot', content: 'Hello, how can I help you?' },
  { id: 'first chat', role: 'user', content: "Hi there! How's it going?" },
  { id: 'first chat', role: 'user', content: "Hi there! How's it going?" },
  { id: 'first chat', role: 'user', content: "Hi there! How's it going?" },
  { id: 'first chat', role: 'user', content: "Hi there! How's it going?" },
  { id: 'first chat', role: 'user', content: "Hi there! How's it going?" },
  { id: 'first chat', role: 'user', content: "Hi there! How's it going?" },
  { id: 'first chat', role: 'user', content: "Hi there! How's it going?" },
  { id: 'first chat', role: 'user', content: "Hi there! How's it going?" },
  { id: 'first chat', role: 'user', content: "Hi there! How's it going?" },
  { id: 'first chat', role: 'user', content: "Hi there! How's it going?" },
  { id: 'first chat', role: 'user', content: "Hi there! How's it going?" },
  { id: 'first chat', role: 'user', content: "Hi there! How's it going?" },
  { id: 'first chat', role: 'user', content: "Hi there! How's it going?" },
  { id: 'first chat', role: 'user', content: "Hi there! How's it going?" },
]

interface Message {
  id: string
  role: string
  content: string
}

export default function Home() {
  const [data, setData] = useState(testData)
  const messagesEndRef = useRef<HTMLDivElement | null>(null)

  const handleFormSubmit = (message: Message) => {
    setData((prevData) => [...prevData, message])
  }

  const handleClearChat = () => {
    setData([
      { id: 'first chat', role: 'bot', content: 'Hello, how can I help you?' },
    ])
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
          <div ref={messagesEndRef} />
        </div>
        {/* Chat form */}
        <div className='flex items-center'>
          <ChatForm onSubmit={handleFormSubmit} />
        </div>
      </div>
    </div>
  )
}
