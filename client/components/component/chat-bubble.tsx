import RobotIcon from '@/components/icon/robot'
import UserIcon from '@/components/icon/user'

interface ChatBubbleProps {
  data: {
    role: string
    content: string
  }
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ data }) => {
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
        className={`chat-bubble text-white ${
          data.role === 'user' ? 'chat-bubble-info' : ''
        }`}
      >
        {data.content}
      </div>
    </div>
  )
}

export default ChatBubble
