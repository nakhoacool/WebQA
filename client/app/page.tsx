'use client'

import { Sidebar } from '@/components/component/sidebar'
import { ChatForm } from '@/components/component/chat-form'
import { useState } from 'react'
export default function Home() {
  const [message, setMessage] = useState("Welcome to the chat. I have modified this");
  
  return (
    <div className='h-screen flex flex-row'>
      <Sidebar />
      <div className='main'>
        <div className='chats'>
          <div className='chat'>
            {message}
          </div>
        </div>
        <div className='chat-footer'>
          <ChatForm setMessage={setMessage}/>
        </div>
      </div>
    </div>
  )
}
