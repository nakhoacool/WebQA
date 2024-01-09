import { AvatarImage, AvatarFallback, Avatar } from '@/components/ui/avatar'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'

import { JSX, SVGProps } from 'react'

export function Sidebar() {
  return (
    <div key='1' className='bg-[#000000] w-[250px] h-full flex flex-col'>
      <div className='flex items-center px-6 py-4 space-x-4 border-b border-gray-700 justify-between'>
        <div className='flex items-center space-x-4'>
          <MessageCircleIcon className='text-gray-400 h-6 w-6' />
          <span className='font-semibold text-lg'>New chat</span>
        </div>
        <PlusIcon className='text-gray-400 h-6 w-6' />
      </div>

      <ScrollArea className='py-2 grow overflow-y-auto'>
        <a
          className='block px-6 py-2 hover:bg-gray-700 truncate text-clip'
          href='#'
        >
          Hello
        </a>
      </ScrollArea>

      <Popover>
        <PopoverTrigger className='flex px-6 py-4 hover:bg-gray-700 border-t border-gray-700 items-center'>
          <Avatar>
            <AvatarImage alt='Guest' src='' />
            <AvatarFallback>G</AvatarFallback>
          </Avatar>
          <span className='font-semibold'>Guest</span>
        </PopoverTrigger>
        <PopoverContent className='w-60'>Hi</PopoverContent>
      </Popover>
    </div>
  )
}

function MessageCircleIcon(
  props: JSX.IntrinsicAttributes & SVGProps<SVGSVGElement>
) {
  return (
    <svg
      {...props}
      xmlns='http://www.w3.org/2000/svg'
      width='24'
      height='24'
      viewBox='0 0 24 24'
      fill='none'
      stroke='currentColor'
      strokeWidth='2'
      strokeLinecap='round'
      strokeLinejoin='round'
    >
      <path d='m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z' />
    </svg>
  )
}

function PlusIcon(props: JSX.IntrinsicAttributes & SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns='http://www.w3.org/2000/svg'
      width='24'
      height='24'
      viewBox='0 0 24 24'
      fill='none'
      stroke='currentColor'
      strokeWidth='2'
      strokeLinecap='round'
      strokeLinejoin='round'
    >
      <path d='M5 12h14' />
      <path d='M12 5v14' />
    </svg>
  )
}
