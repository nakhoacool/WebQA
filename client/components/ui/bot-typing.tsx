import RobotIcon from '@/components/icon/robot'

function BotTyping() {
  return (
    <div className='p-4 flex'>
      <div className='rounded-full h-8 w-8 flex items-center justify-center mr-2'>
        <RobotIcon />
      </div>
      <div className='rounded-lg bg-gray-700 px-4 py-2 inline-block max-w-xs text-sm'>
        <div className='animate-pulse bg-gray-500 rounded-full h-2 w-2 mr-1 inline-block'></div>
        <div className='animate-pulse bg-gray-500 rounded-full h-2 w-2 mr-1 inline-block'></div>
        <div className='animate-pulse bg-gray-500 rounded-full h-2 w-2 inline-block'></div>
      </div>
    </div>
  )
}

export default BotTyping