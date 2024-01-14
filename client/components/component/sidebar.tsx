'use client'
import { AvatarImage, AvatarFallback, Avatar } from '@/components/ui/avatar'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Button } from '@/components/ui/button'
import React, { useState } from 'react'
import SidebarItem from '@/components/component/sidebar-item'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'

import { JSX, SVGProps } from 'react'

export function Sidebar() {
  const [items, setItems] = useState(['Hellodadawdawdawdawdwa', 'Hello'])
  const handleRemove = (indexToRemove: number) => {
    setItems(items.filter((_, index) => index !== indexToRemove))
  }

  return (
    <div key='1' className='bg-[#000000] w-[250px] h-full flex flex-col'>
      <Button
        variant='outline'
        className='flex items-center px-6 py-4 space-x-4 border-b border-gray-700 justify-between'
      >
        <div className='flex items-center space-x-4'>
          <span className='font-semibold text-lg'>New chat</span>
        </div>
        <PlusIcon className='text-gray-400 h-6 w-6' />
      </Button>

      <ScrollArea className='py-3 grow overflow-y-auto'>
        {items.map((text, index) => (
          <SidebarItem
            key={index}
            text={text}
            onRemove={() => handleRemove(index)}
          />
        ))}
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
