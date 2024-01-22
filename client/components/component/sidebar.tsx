import React from 'react'
import { AvatarImage, AvatarFallback, Avatar } from '@/components/ui/avatar'
import PlusIcon from '@/components/icon/plus'
import SidebarItem from './sidebar-item'
interface SidebarProps {
  chatHistory: any[]
  handleClearChat: () => void
  handleSidebarItemClick: (id: string) => void
  handleRemoveChatHistory: (id: string) => void
}

const Sidebar: React.FC<SidebarProps> = ({
  chatHistory,
  handleClearChat,
  handleSidebarItemClick,
  handleRemoveChatHistory,
}) => {
  return (
    <div className='flex flex-col w-64 border-r border-gray-700'>
      <div className='px-4 py-2 flex items-center justify-between border-b border-gray-700'>
        <h2 className='text-lg font-semibold'>New chat</h2>
        <button
          className='p-2 rounded-full hover:bg-gray-600 focus:outline-none focus:ring hover:scale-105 transition-transform duration-200 ease-in-out'
          onClick={handleClearChat}
        >
          <PlusIcon className='text-white h-6 w-6' />
        </button>
      </div>
      <div className='overflow-y-auto'>
        {chatHistory.map((item, index) => (
          <SidebarItem
            key={item.id}
            item={item}
            index={index}
            handleSidebarItemClick={handleSidebarItemClick}
            handleRemoveChatHistory={handleRemoveChatHistory}
          />
        ))}
      </div>
      <div className='px-4 py-2 flex items-center space-x-2 border-t border-gray-700 mt-auto'>
        <Avatar>
          <AvatarImage alt='Guest' src='/placeholder.svg?height=32&width=32' />
          <AvatarFallback>G</AvatarFallback>
        </Avatar>
        <span className='text-sm'>Guest</span>
      </div>
    </div>
  )
}

export default Sidebar
