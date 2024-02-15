import React from 'react'
import { AvatarImage, AvatarFallback, Avatar } from '@/components/ui/avatar'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import PlusIcon from '@/components/icon/plus'
import LogOutIcon from '@/components/icon/logout'
import SidebarItem from '@/components/component/sidebar-item'
import { signOut } from 'next-auth/react'
import { ChatHistory } from '@/lib/types'
interface SidebarProps {
  session: any
  chatHistory: ChatHistory[]
  handleClearChat: () => void
  handleSidebarItemClick: (id: string) => void
  handleRemoveChatHistory: (id: string) => void
  activeChatHistoryId: string | null
}

const Sidebar: React.FC<SidebarProps> = ({
  session,
  chatHistory,
  handleClearChat,
  handleSidebarItemClick,
  handleRemoveChatHistory,
  activeChatHistoryId,
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
        {chatHistory.map((item) => (
          <SidebarItem
            key={item.id}
            item={item}
            handleSidebarItemClick={handleSidebarItemClick}
            handleRemoveChatHistory={handleRemoveChatHistory}
            activeChatHistoryId={activeChatHistoryId}
          />
        ))}
      </div>
      <Popover>
        <PopoverTrigger className='px-4 py-2 flex items-center space-x-2 border-t border-gray-700 mt-auto'>
          <Avatar>
            <AvatarImage
              alt='user profile image'
              src= {session?.user?.image}
            />
            <AvatarFallback>
              <span>{session?.user?.email[0].toUpperCase()}</span>
            </AvatarFallback>
          </Avatar>
          <span className='text-sm'>{session?.user?.email}</span>
        </PopoverTrigger>
        <PopoverContent className='w-[15rem] pl-2 pr-2'>
          <button
            onClick={() => signOut()}
            className='py-2 hover:bg-gray-700 w-full flex items-center rounded space-x-2'
          >
            <LogOutIcon className='text-white' />
            <span>Sign out</span>
          </button>
        </PopoverContent>
      </Popover>
    </div>
  )
}

export default Sidebar
