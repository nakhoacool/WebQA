'use client'
import { Sidebar } from '@/components/component/sidebar'
import ChatBubble from '@/components/ui/chat-bubble'
import { ChatForm } from '@/components/component/chat-form'
import React, { useState, useEffect, useRef, useReducer } from 'react'

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

type Action = { type: 'add_message'; message: Message } | { type: 'clear_chat' }

const chatReducer = (state: Message[], action: Action) => {
  switch (action.type) {
    case 'add_message':
      return [...state, action.message]
    case 'clear_chat':
      return [
        {
          id: 'first chat',
          role: 'bot',
          content: 'Hello, how can I help you?',
        },
      ]
    default:
      return state
  }
}

export default function Home() {
  const [data, dispatch] = useReducer(chatReducer, testData)
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
