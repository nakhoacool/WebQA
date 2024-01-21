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
    if (data.role === 'bot') {
      let messageArray = data.content.split(' ')
      let i = 0
      const intervalId = setInterval(() => {
        setCurrentMessage((prev) => prev + ' ' + messageArray[i])
        i++
        if (i === messageArray.length) {
          clearInterval(intervalId)
        }
      }, 20) // Adjust the interval to control the speed of typing
      return () => clearInterval(intervalId)
    } else {
      setCurrentMessage(data.content)
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
