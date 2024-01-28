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
    <div className={`p-4 flex ${data.role === 'bot' ? '' : 'justify-end'}`}>
      {data.role === 'bot' && (
        <div className='rounded-full h-8 w-8 flex items-center justify-center mr-2'>
          <RobotIcon />
        </div>
      )}
      <div
        className={`rounded-lg w-full ${
          data.role === 'bot' ? 'bg-gray-700 max-w-100' : 'bg-blue-600 max-w-80'
        } px-4 py-2 inline-block text-base text-justify`}
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
}

export default ChatBubble;