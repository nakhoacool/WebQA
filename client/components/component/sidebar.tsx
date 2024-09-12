import { signOut, useSession } from 'next-auth/react'
import { useContext } from 'react'
import { ChatContext } from '@/contexts/ChatContext'
import { AvatarFallback, Avatar } from '@/components/ui/avatar'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import PlusIcon from '@/components/icon/plus'
import LogOutIcon from '@/components/icon/logout'
import SidebarItem from '@/components/component/sidebar-item'

export default function Sidebar() {
  const { data: session } = useSession()
  const context = useContext(ChatContext)

  if (!context) {
    throw new Error('useContext must be used within a ChatProvider')
  }

  const { handleClearChat, chatHistory } = context
  return (
    <div className='flex flex-col w-64 border-r bg-[#F9F9F9]'>
      <div className='p-2'>
        <button
          className='btn w-full flex justify-between items-center px-4 py-2 space-x-2'
          onClick={handleClearChat}
        >
          <span>New chat</span>
          <PlusIcon />
        </button>
      </div>
      <div className='divider mt-[-1px] mb-[-2px]'></div>
      <div className='overflow-y-auto p-2'>
        {chatHistory.map((item) => (
          <SidebarItem key={item.id} item={item} />
        ))}
      </div>
      <Popover>
        <PopoverTrigger className='px-4 py-2 flex items-center space-x-2 border-t mt-auto'>
          <Avatar>
            <AvatarFallback className='text-white bg-gray-500'>
              <span>{session?.user.email?.[0]?.toUpperCase()}</span>
            </AvatarFallback>
          </Avatar>
          <p className='text-sm truncate text-clip text-black'>
            {session?.user.email}
          </p>
        </PopoverTrigger>
        <PopoverContent className='w-[15rem] px-2'>
          <button
            onClick={() => signOut({ callbackUrl: '/', redirect: true })}
            className='py-2 hover:bg-[#C7C8C8] w-full flex items-center rounded space-x-2'
          >
            <LogOutIcon className='text-black' />
            <span>Sign out</span>
          </button>
        </PopoverContent>
      </Popover>
    </div>
  )
}
