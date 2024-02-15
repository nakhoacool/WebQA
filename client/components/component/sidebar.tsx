import { signOut } from 'next-auth/react'
import { AvatarImage, AvatarFallback, Avatar } from '@/components/ui/avatar'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import PlusIcon from '@/components/icon/plus'
import LogOutIcon from '@/components/icon/logout'
import SidebarItem from '@/components/component/sidebar-item'
import { SidebarProps } from '@/lib/types'

export default function Sidebar({
  session,
  chatHistory,
  handleClearChat,
  handleSidebarItemClick,
  handleRemoveChatHistory,
  activeChatHistoryId,
}: SidebarProps) {
  return (
    <div className='flex flex-col w-64 border-r border-[#282828] bg-[#171717]'>
      <div className='border-b border-[#282828] p-2'>
        <button
          className='btn bg-[#1c1528] hover:bg-[#35255c] w-full flex justify-between items-center px-4 py-2 space-x-2'
          onClick={handleClearChat}
        >
          <span>New chat</span>
          <PlusIcon />
        </button>
      </div>
      <div className='overflow-y-auto p-2'>
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
        <PopoverTrigger className='px-4 py-2 flex items-center space-x-2 border-t border-[#282828] hover:bg-[#35255c] bg-[#1c1528] mt-auto'>
          <Avatar>
            <AvatarImage alt='user profile image' src={session?.user?.image} />
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
