import React, { useState, useEffect } from 'react'
import RobotIcon from '@/components/icon/robot'
import UserIcon from '@/components/icon/user'

interface ChatBubbleProps {
  data: {
    id: string
    role: string
    content: string
  }
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ data }) => {
  const [currentMessage, setCurrentMessage] = useState('')
  useEffect(() => {
    let timeoutId: NodeJS.Timeout | null = null
    if (data.role === 'bot') {
      let messageArray = data.content.split(' ')
      let i = 0
      const addWord = () => {
        setCurrentMessage((prev) => prev + ' ' + messageArray[i])
        i++
        if (i < messageArray.length) {
          timeoutId = setTimeout(() => requestAnimationFrame(addWord), 50)
        }
      }
      // Start the typing effect
      addWord()
    } else {
      setCurrentMessage(data.content)
    }

    // Cleanup function
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
    }
  }, [data])
  return (
    <div className={`p-4 flex ${data.role === 'bot' ? '' : 'justify-end'}`}>
      {data.role === 'bot' && (
        <div className='rounded-full h-8 w-8 flex items-center justify-center mr-2'>
          <RobotIcon />
        </div>
      )}
      <div
        className={`rounded-lg ${
          data.role === 'bot' ? 'bg-gray-700' : 'bg-blue-600'
        } px-4 py-2 inline-block max-w-xs text-sm text-justify`}
      >
        {currentMessage}
      </div>
      {data.role === 'user' && (
        <div className='rounded-full h-8 w-8 flex items-center justify-center ml-2'>
          <UserIcon />
        </div>
      )}
    </div>
  )
}
export default ChatBubble
