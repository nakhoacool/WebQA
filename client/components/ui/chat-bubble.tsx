import React from 'react'
import RobotIcon from '@/components/icon/robot'
import UserIcon from '@/components/icon/user'

interface ChatBubbleProps {
  data: {
    id: string
    role: string
    content: string
  }
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ data }) => (
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
      {data.content}
    </div>
    {data.role === 'user' && (
      <div className='rounded-full h-8 w-8 flex items-center justify-center ml-2'>
        <UserIcon />
      </div>
    )}
  </div>
)
export default ChatBubble
