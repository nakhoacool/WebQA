'use client'
import { useSession } from 'next-auth/react'
import { redirect } from 'next/navigation'
import { useContext } from 'react'
import { ChatContext } from '@/contexts/ChatContext'
import ChatBubble from '@/components/component/chat-bubble'
import ChatForm from '@/components/component/chat-form'
import BotTyping from '@/components/ui/bot-typing'
import Sidebar from '@/components/component/sidebar'
import Loading from '@/components/ui/loading'

export default function Home() {
  const context = useContext(ChatContext)

  if (!context) {
    throw new Error('useContext must be used within a ChatProvider')
  }

  const { data, isBotTyping, messagesEndRef } = context

  const { status } = useSession({
    required: true,
    onUnauthenticated() {
      redirect('/auth/signin')
    },
  })

  if (status === 'loading') {
    return <Loading />
  }

  return (
    <div className='flex h-screen text-white'>
      {/* Sidebar */}
      <Sidebar />
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
          <ChatForm />
        </div>
      </div>
    </div>
  )
}

Home.requireAuth = true
