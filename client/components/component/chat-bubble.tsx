import RobotIcon from '@/components/icon/robot'
import UserIcon from '@/components/icon/user'
import { ChatBubbleProps } from '@/lib/types'

export default function ChatBubble({ data }: ChatBubbleProps) {
  return (
    <div
      className={`p-4 chat ${data.role === 'bot' ? 'chat-start' : 'chat-end'}`}
    >
      <div className='chat-image avatar'>
        <div className='w-9 rounded-full'>
          {data.role === 'bot' ? <RobotIcon /> : <UserIcon />}
        </div>
      </div>
      <div className='chat-header'>{data.role === 'bot' ? 'Bot' : 'User'}</div>
      <div
        className={`chat-bubble max-w-80 text-white ${
          data.role === 'user' ? 'chat-bubble-info' : ''
        }`}
      >
        {data.content}
      </div>
    </div>
  )
}
