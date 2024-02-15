import RobotIcon from '@/components/icon/robot'

function BotTyping() {
  return (
    <div className='p-4 chat chat-start'>
      <div className='chat-image avatar'>
        <div className='w-9 rounded-full'>
          <RobotIcon />
        </div>
      </div>
      <div className='chat-header'>Bot</div>
      <div className='chat-bubble max-w-80 break-all'>
        <div className='animate-pulse bg-gray-500 rounded-full h-2 w-2 mr-1 inline-block'></div>
        <div className='animate-pulse bg-gray-500 rounded-full h-2 w-2 mr-1 inline-block'></div>
        <div className='animate-pulse bg-gray-500 rounded-full h-2 w-2 inline-block'></div>
      </div>
    </div>
  )
}

export default BotTyping