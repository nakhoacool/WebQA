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
import ShieldIcon from '@/components/icon/shield'
import SidebarItem from '@/components/component/sidebar-item'
import Link from 'next/link'

export default function Sidebar() {
  const { data: session } = useSession()
  const context = useContext(ChatContext)

  if (!context) {
    throw new Error('useContext must be used within a ChatProvider')
  }

  const { handleClearChat, chatHistory } = context
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
          <SidebarItem key={item.id} item={item} />
        ))}
      </div>
      <Popover>
        <PopoverTrigger className='px-4 py-2 flex items-center space-x-2 border-t border-[#282828] hover:bg-[#35255c] bg-[#1c1528] mt-auto'>
          <Avatar>
            <AvatarFallback>
              <span>{session?.user.email?.[0]?.toUpperCase()}</span>
            </AvatarFallback>
          </Avatar>
          <span className='text-sm truncate text-clip'>
            {session?.user.email}
          </span>
        </PopoverTrigger>
        <PopoverContent className='w-[15rem] px-2'>
          {session?.user.role === 'admin' && (
            <Link
              href='/admin'
              className='py-2 hover:bg-gray-700 w-full flex items-center rounded space-x-2 border-b border-[#424142]'
            >
              <ShieldIcon className='text-white' />
              <span>Admin Dashboard</span>
            </Link>
          )}
          <button
            onClick={() => signOut({ callbackUrl: '/', redirect: true })}
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
