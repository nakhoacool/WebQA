'use client'
import { useSession } from 'next-auth/react'
import { redirect } from 'next/navigation'
import { useContext, useEffect } from 'react'
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

  const {
    data,
    isBotTyping,
    messagesEndRef,
    selectedOption,
    setSelectedOption,
    isNewChat,
    setUserID,
  } = context

  const { status, data: Session } = useSession({
    required: true,
    onUnauthenticated() {
      redirect('/auth/signin')
    },
  })

  useEffect(() => {
    if (Session?.user.id) {
      setUserID(Session.user.id)
    }
  }, [Session, setUserID])

  if (status === 'loading') {
    return <Loading />
  }

  return (
    <div className='flex h-screen text-white'>
      {/* Sidebar */}
      <Sidebar />
      {/* Chat */}
      <div className='flex-1 flex flex-col'>
        <div className='flex items-center space-x-4 p-4 bg-[#00035B]'>
          <h1 className='text-xl font-bold'>Chatbot</h1>
          <select
            value={selectedOption}
            onChange={(e) => setSelectedOption(e.target.value)}
            disabled={!isNewChat}
            className='bg-[#1c1528] text-white rounded'
          >
            <option value='tdt'>TDT</option>
            <option value='ueh'>UEH</option>
            <option value='raptor_tdt'>TDT (RAPTOR)</option>
            <option value='raptor_ueh'>UEH (RAPTOR)</option>
          </select>
        </div>
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
